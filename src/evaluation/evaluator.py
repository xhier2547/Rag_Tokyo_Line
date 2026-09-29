"""
src/evaluation/evaluator.py
===========================
โมดูลประเมินผลเชิงปริมาณและคุณภาพสำหรับ Tokyo Smart Transit & Tourism Hybrid Graph RAG
(Phase 6: Evaluation & Analysis - 10 คะแนน)

เมตริกการวัดผล:
1. Latency (sec): เวลาประมวลผลต่อคำถาม
2. Grounding & Faithfulness: ตรวจสอบการมีแท็ก [อ้างอิง: ...] และความสอดคล้องกับบริบท
3. Graph Context Utilization: ตรวจสอบว่าโจทย์ที่ต้องการ Graph มีการดึงข้อมูลจาก Knowledge Graph จริงหรือไม่
4. Citation Density: จำนวนแหล่งอ้างอิงที่ระบุในคำตอบ
5. Success Rate: อัตราการตอบสำเร็จโดยไม่เกิด Exception หรือ Timeout
"""

import os
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

from src.service.rag_service import TokyoRAGService, RAGResponse
from src.llm.prompts import extract_citations


class EvaluationItemResult(BaseModel):
    """ผลการทดสอบต่อหนึ่งข้อคำถาม"""
    question_id: int
    category: str
    category_name: str
    query: str
    requires_graph: bool
    mode: str
    model_name: str
    intent_detected: str
    answer: str
    citations: List[str] = Field(default_factory=list)
    has_citations: bool
    citation_count: int
    graph_used: bool
    latency_sec: float
    is_cached: bool
    success: bool
    error: Optional[str] = None


class BenchmarkSummary(BaseModel):
    """สรุปผลการประเมินภาพรวม"""
    mode: str
    model_name: str
    total_evaluated: int
    success_rate_percent: float
    citation_rate_percent: float
    avg_latency_sec: float
    avg_citations_per_query: float
    graph_utilization_percent: float
    category_breakdown: Dict[str, Dict[str, Any]]


class TokyoRAGEvaluator:
    """
    คลาสสำหรับรัน Benchmark และวิเคราะห์ผลลัพธ์
    """

    def __init__(
        self,
        service: Optional[TokyoRAGService] = None,
        benchmark_file: str = "data/benchmark_100_questions.json"
    ):
        self.benchmark_file = benchmark_file
        self._service = service

    @property
    def service(self) -> TokyoRAGService:
        if self._service is None:
            self._service = TokyoRAGService()
        return self._service


    def load_benchmark_questions(
        self,
        category: Optional[str] = None,
        sample_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        โหลดข้อสอบจากไฟล์ JSON
        - category: กรองเฉพาะหมวด เช่น 'F', 'G', 'J'
        - sample_size: สุ่ม/เลือกเฉพาะ N ข้อแรกของแต่ละหมวดเพื่อประหยัดเวลา
        """
        if not os.path.exists(self.benchmark_file):
            raise FileNotFoundError(f"ไม่พบไฟล์ชุดคำถามที่: {self.benchmark_file}")

        with open(self.benchmark_file, "r", encoding="utf-8") as f:
            all_questions: List[Dict[str, Any]] = json.load(f)

        filtered = all_questions
        if category:
            filtered = [q for q in filtered if q["category"].upper() == category.upper()]

        if sample_size and sample_size < len(filtered):
            # เลือกแบบกระจายครบทุกหมวดเท่าๆ กัน
            categories = sorted(list(set(q["category"] for q in filtered)))
            per_cat = max(1, sample_size // len(categories))
            sampled = []
            for cat in categories:
                cat_items = [q for q in filtered if q["category"] == cat]
                sampled.extend(cat_items[:per_cat])
            return sampled[:sample_size]

        return filtered

    def evaluate_single_query(
        self,
        question: Dict[str, Any],
        mode: str = "gemini"
    ) -> EvaluationItemResult:
        """
        ประเมินผลคำถาม 1 ข้อ พร้อมดึงเมตริกเชิงลึก
        """
        q_id = question["id"]
        cat = question["category"]
        cat_name = question.get("category_name", "")
        query = question["query"]
        req_graph = question.get("requires_graph", False)

        try:
            resp: RAGResponse = self.service.answer_query(
                query=query,
                mode=mode,
                force_refresh=True  # ในการทดสอบ Benchmark บังคับให้ประมวลผลสด ไม่ใช้แคช
            )

            citations = resp.citations or extract_citations(resp.answer)
            has_cit = len(citations) > 0
            graph_used = bool(resp.graph_context and len(resp.graph_context.strip()) > 0)

            return EvaluationItemResult(
                question_id=q_id,
                category=cat,
                category_name=cat_name,
                query=query,
                requires_graph=req_graph,
                mode=mode,
                model_name=resp.model_name,
                intent_detected=resp.intent,
                answer=resp.answer,
                citations=citations,
                has_citations=has_cit,
                citation_count=len(citations),
                graph_used=graph_used,
                latency_sec=resp.latency_sec,
                is_cached=resp.is_cached,
                success=True,
                error=None
            )

        except Exception as e:
            return EvaluationItemResult(
                question_id=q_id,
                category=cat,
                category_name=cat_name,
                query=query,
                requires_graph=req_graph,
                mode=mode,
                model_name="unknown",
                intent_detected="ERROR",
                answer=f"เกิดข้อผิดพลาด: {str(e)}",
                citations=[],
                has_citations=False,
                citation_count=0,
                graph_used=False,
                latency_sec=0.0,
                is_cached=False,
                success=False,
                error=str(e)
            )

    def run_benchmark(
        self,
        questions: List[Dict[str, Any]],
        mode: str = "gemini",
        output_file: Optional[str] = None,
        delay_sec: float = 0.5,
        force_fresh: bool = False
    ) -> Tuple[List[EvaluationItemResult], BenchmarkSummary]:
        """
        รัน Benchmark ตามรายการคำถามที่กำหนด
        มีระบบ Flush ทีละข้อ ป้องกันเครื่องค้างและบันทึก Checkpoint ต่อเนื่อง
        """
        if output_file is None:
            output_file = f"data/benchmark_results_{mode}.json"

        # โหลดผลเดิมหากมี (Resume Support) เว้นแต่จะระบุ force_fresh=True
        results_map: Dict[int, EvaluationItemResult] = {}
        if not force_fresh and os.path.exists(output_file):
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                    for item in old_data.get("details", []):
                        results_map[item["question_id"]] = EvaluationItemResult(**item)
                print(f"[TokyoRAGEvaluator] โหลดผลเดิม {len(results_map)} ข้อจาก {output_file}")
            except Exception:
                pass

        total_questions = len(questions)
        for idx, q in enumerate(questions, 1):
            q_id = q["id"]
            if q_id in results_map:
                print(f"[{idx}/{total_questions}] ข้ามข้อที่ {q_id} (ประเมินแล้ว)")
                continue

            print(f"[{idx}/{total_questions}] กำลังทดสอบข้อ {q_id} (หมวด {q['category']}): '{q['query'][:35]}...'")
            res = self.evaluate_single_query(q, mode=mode)
            results_map[q_id] = res

            # บันทึก Checkpoint ลงไฟล์ทันที
            self._save_checkpoint(output_file, mode, list(results_map.values()))

            # หน่วงเวลาเพื่อไม่ให้ CPU/API โหลดหนัก
            if delay_sec > 0 and idx < total_questions:
                time.sleep(delay_sec)

        # สรุปผลลัพธ์
        ordered_results = [results_map[q["id"]] for q in questions if q["id"] in results_map]
        summary = self.calculate_summary(ordered_results, mode=mode)

        # บันทึกไฟล์สมบูรณ์
        self._save_checkpoint(output_file, mode, ordered_results, summary=summary)
        return ordered_results, summary

    def calculate_summary(
        self,
        results: List[EvaluationItemResult],
        mode: str
    ) -> BenchmarkSummary:
        """คำนวณสถิติภาพรวมและการแจกแจงตามหมวดหมู่"""
        total = len(results)
        if total == 0:
            return BenchmarkSummary(
                mode=mode,
                model_name="N/A",
                total_evaluated=0,
                success_rate_percent=0.0,
                citation_rate_percent=0.0,
                avg_latency_sec=0.0,
                avg_citations_per_query=0.0,
                graph_utilization_percent=0.0,
                category_breakdown={}
            )

        success_count = sum(1 for r in results if r.success)
        citation_count = sum(1 for r in results if r.has_citations)
        total_lat = sum(r.latency_sec for r in results if r.success)
        total_cits = sum(r.citation_count for r in results if r.success)
        graph_count = sum(1 for r in results if r.graph_used)

        model_name = results[0].model_name if results else mode

        # แยกตามหมวดหมู่
        cat_stats: Dict[str, Dict[str, Any]] = {}
        for r in results:
            cat = r.category
            if cat not in cat_stats:
                cat_stats[cat] = {
                    "category_name": r.category_name,
                    "total": 0,
                    "success": 0,
                    "with_citations": 0,
                    "graph_used": 0,
                    "total_latency": 0.0
                }
            cat_stats[cat]["total"] += 1
            if r.success:
                cat_stats[cat]["success"] += 1
                cat_stats[cat]["total_latency"] += r.latency_sec
            if r.has_citations:
                cat_stats[cat]["with_citations"] += 1
            if r.graph_used:
                cat_stats[cat]["graph_used"] += 1

        cat_breakdown = {}
        for cat, st in cat_stats.items():
            tot = st["total"]
            succ = st["success"]
            cat_breakdown[cat] = {
                "name": st["category_name"],
                "total": tot,
                "avg_latency": round(st["total_latency"] / max(1, succ), 3),
                "citation_rate_pct": round((st["with_citations"] / tot) * 100, 1),
                "graph_used_pct": round((st["graph_used"] / tot) * 100, 1)
            }

        return BenchmarkSummary(
            mode=mode,
            model_name=model_name,
            total_evaluated=total,
            success_rate_percent=round((success_count / total) * 100, 1),
            citation_rate_percent=round((citation_count / total) * 100, 1),
            avg_latency_sec=round(total_lat / max(1, success_count), 3),
            avg_citations_per_query=round(total_cits / max(1, success_count), 2),
            graph_utilization_percent=round((graph_count / total) * 100, 1),
            category_breakdown=cat_breakdown
        )

    def _save_checkpoint(
        self,
        filepath: str,
        mode: str,
        results: List[EvaluationItemResult],
        summary: Optional[BenchmarkSummary] = None
    ) -> None:
        """บันทึกผลลงไฟล์ JSON"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data = {
            "mode": mode,
            "total_items": len(results),
            "summary": summary.model_dump() if summary else None,
            "details": [r.model_dump() for r in results]
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
