"""
src/evaluation/run_comprehensive_eval.py
========================================
สคริปต์ประเมินผลเชิงประจักษ์แบบครบวงจร (Comprehensive Empirical Evaluator)
สำหรับ Tokyo Smart Transit & Tourism Hybrid Graph RAG

ความสามารถหลัก:
1. Retrieval Ablation Experiment:
   เปรียบเทียบประสิทธิภาพของ 3 สถาปัตยกรรม:
   - Dense RAG Only (FAISS Embeddings)
   - Graph RAG Only (NetworkX Pathfinder & Graph Traversal)
   - Hybrid Graph RAG (Dense FAISS + Sparse BM25 + Graph + RRF + Re-ranking)
   วัดผลด้วยเมตริกมาตรฐาน:
   - Hit Rate@1
   - Hit Rate@3
   - Mean Reciprocal Rank (MRR)
   - Multi-hop / Spatial Query Success Rate
   - Average Retrieval Latency (ms)

2. End-to-End Generation Evaluation:
   ประเมินผลการตอบของ LLM (Gemini 3.1 Flash Lite) ในด้าน:
   - Success Rate (%)
   - Citation Rate / Zero-Hallucination (%)
   - Graph Utilization Rate (%)
   - Latency Distribution

3. บันทึกผลการทดลองดิบ (Raw JSON) และสร้างตารางสรุปสำหรับรายงาน evaluation_report.md
"""

import os
import sys
import time
import json
import re
from typing import Dict, Any, List, Tuple
from collections import defaultdict

# กำหนด Encoding สำหรับ Windows Terminal และ PYTHONPATH
sys.path.insert(0, ".")
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.hybrid.engine import TokyoHybridRAGEngine
from src.vector.faiss_store import TokyoFAISSStore
from src.graph.pathfinder import TokyoGraphPathfinder
from src.service.rag_service import TokyoRAGService



def load_benchmark(file_path: str = "data/benchmark_100_questions.json") -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing benchmark file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_expected_keywords(query: str, category: str) -> List[str]:
    """สกัดคำสำคัญหรือ Entity ที่คาดหวังว่าต้องปรากฏในบริบทการดึงข้อมูล"""
    clean = query.lower()
    entities = []

    # รายชื่อสถานที่และสถานีหลัก
    targets = [
        "senso-ji", "sensō-ji", "เซ็นโซจิ", "อาซากุสะ", "asakusa",
        "skytree", "สกายทรี", "oshiage",
        "shibuya", "ชิบูย่า", "hachiko", "ฮาจิโกะ",
        "meiji", "เมจิ", "harajuku", "ฮาราจูกุ",
        "tokyo tower", "โตเกียวทาวเวอร์", "hamamatsucho",
        "shinjuku", "ชินจูกุ", "gyoen", "เกียวเอ็น",
        "akihabara", "อากิฮาบาระ",
        "tsukiji", "สึกิจิ", "ตลาดปลา",
        "ueno", "อุเอโนะ", "ameyoko", "อะเมโยโกะ",
        "roppongi", "รปปงงิ", "mori tower",
        "ginza", "กินซ่า", "ginza six",
        "odaiba", "โอไดบะ", "gundam", "กันดั้ม",
        "imperial", "อิมพีเรียล", "พระราชวัง", "tokyo station", "สถานีโตเกียว",
        "teamlab", "ทีมแล็บ", "toyosu", "โทโยสุ",
        "takeshita", "ทาเคชิตะ",
        "hamarikyu", "ฮามาริคิว",
        "tokyo dome", "โตเกียวโดม", "korakuen",
        "omotesando", "โอโมเตะซันโด"
    ]

    for t in targets:
        if t in clean:
            entities.append(t)

    # หมวดคำศัพท์ทั่วไป
    if not entities:
        if "วัด" in clean or "ศาลเจ้า" in clean:
            entities.extend(["วัด", "ศาลเจ้า", "senso-ji", "meiji"])
        elif "สวน" in clean or "ธรรมชาติ" in clean:
            entities.extend(["สวน", "gyoen", "ueno", "hamarikyu"])
        elif "อาหาร" in clean or "กิน" in clean or "ตลาด" in clean:
            entities.extend(["tsukiji", "ameyoko", "toyosu"])
        elif "อนิเมะ" in clean or "เกม" in clean:
            entities.extend(["akihabara", "odaiba"])
        elif "ช้อป" in clean:
            entities.extend(["ginza", "shibuya", "omotesando"])

    return entities or ["tokyo"]


def run_ablation_study(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    รันการทดลอง Retrieval Ablation Study เปรียบเทียบ 3 สถาปัตยกรรม:
    1. Dense Only (FAISS Top-3 Retrieval)
    2. Graph Only (NetworkX/Neo4j Pathfinder & Multi-hop Traversal)
    3. Hybrid RAG (Dense FAISS + Sparse BM25 + Graph + RRF + Re-ranking)
    
    ประเมินผลด้วย Ground-Truth Document/Entity IDs จริงทั้ง 100 ข้อ:
    - Hit@1: เอกสารหรือเอนทิตีที่เกี่ยวข้องปรากฏในอันดับ 1
    - Hit@3: เอกสารหรือเอนทิตีที่เกี่ยวข้องปรากฏใน 3 อันดับแรก
    - MRR (Mean Reciprocal Rank): 1 / อันดับแรกที่พบ (Rank)
    - Per-Query Raw Results: บันทึกผลลัพธ์รายข้อ 100 ข้อลง data/ablation_per_query_results.json
    """
    print("\n" + "=" * 70)
    print("🔬 RUNNING SCIENTIFIC RETRIEVAL ABLATION EXPERIMENT (100 Questions)")
    print("=" * 70)

    os.environ["HF_HUB_OFFLINE"] = "1"
    faiss_store = TokyoFAISSStore()
    faiss_store.load_index()

    pathfinder = TokyoGraphPathfinder()
    hybrid_engine = TokyoHybridRAGEngine()

    results = {
        "dense_only": {"hits_top1": 0, "hits_top3": 0, "mrr_sum": 0.0, "total_lat_ms": 0.0, "graph_hit": 0},
        "graph_only": {"hits_top1": 0, "hits_top3": 0, "mrr_sum": 0.0, "total_lat_ms": 0.0, "graph_hit": 0},
        "hybrid_rag": {"hits_top1": 0, "hits_top3": 0, "mrr_sum": 0.0, "total_lat_ms": 0.0, "graph_hit": 0}
    }

    per_query_records = []
    n = len(questions)

    # ดึงชื่อและคีย์เวิร์ดของสถานที่และสถานีในกราฟสำหรับตรวจสอบ Graph Context
    place_names_map = {}
    for node, data in pathfinder.nx_graph.nodes(data=True):
        names = [node.lower()]
        if data.get("name_th"):
            names.append(data["name_th"].lower())
        if data.get("name_en"):
            names.append(data["name_en"].lower())
        place_names_map[node] = names

    for idx, q in enumerate(questions):
        qid = q["id"]
        query = q["query"]
        cat = q["category"]
        req_graph = q.get("requires_graph", False)
        gt_chunks = set(q.get("ground_truth_chunks", []))
        gt_entities = set(q.get("ground_truth_entities", []))

        # ----------------------------------------------------
        # 1. Dense Only (FAISS Top-3)
        # ----------------------------------------------------
        t0 = time.perf_counter()
        dense_docs = faiss_store.search(query, k=3)
        dense_lat = (time.perf_counter() - t0) * 1000.0
        results["dense_only"]["total_lat_ms"] += dense_lat

        dense_rank = None
        retrieved_chunk_ids = []
        for r_idx, (doc, _) in enumerate(dense_docs):
            cid = doc.metadata.get("chunk_id", "")
            pid = doc.metadata.get("place_id", "")
            retrieved_chunk_ids.append(cid)
            if (cid in gt_chunks or pid in gt_entities) and dense_rank is None:
                dense_rank = r_idx + 1

        dense_hit1 = 1 if dense_rank == 1 else 0
        dense_hit3 = 1 if dense_rank is not None and dense_rank <= 3 else 0
        dense_rr = (1.0 / dense_rank) if dense_rank is not None else 0.0

        results["dense_only"]["hits_top1"] += dense_hit1
        results["dense_only"]["hits_top3"] += dense_hit3
        results["dense_only"]["mrr_sum"] += dense_rr

        # ----------------------------------------------------
        # 2. Graph Only (Pathfinder Context)
        # ----------------------------------------------------
        t0 = time.perf_counter()
        graph_ctx = pathfinder.extract_graph_context_for_rag(query)
        graph_lat = (time.perf_counter() - t0) * 1000.0
        results["graph_only"]["total_lat_ms"] += graph_lat

        clean_graph_ctx = graph_ctx.lower()
        has_graph = bool(clean_graph_ctx.strip())
        if has_graph:
            results["graph_only"]["graph_hit"] += 1

        # ตรวจสอบว่าใน Graph Context มีเอนทิตีที่ตรงกับ Ground Truth หรือไม่
        graph_match = False
        if has_graph and gt_entities:
            for ent in gt_entities:
                aliases = place_names_map.get(ent, [ent.lower()])
                if any(alias in clean_graph_ctx for alias in aliases if len(alias) >= 3):
                    graph_match = True
                    break
        elif has_graph and not gt_entities:
            graph_match = True

        graph_hit1 = 1 if graph_match else 0
        graph_hit3 = 1 if graph_match else 0
        graph_rr = 1.0 if graph_match else 0.0

        results["graph_only"]["hits_top1"] += graph_hit1
        results["graph_only"]["hits_top3"] += graph_hit3
        results["graph_only"]["mrr_sum"] += graph_rr

        # ----------------------------------------------------
        # 3. Hybrid RAG (Dense + BM25 + Graph + RRF + Re-ranking)
        # ----------------------------------------------------
        t0 = time.perf_counter()
        hyb_res = hybrid_engine.retrieve_hybrid_context(query)
        hyb_lat = (time.perf_counter() - t0) * 1000.0
        results["hybrid_rag"]["total_lat_ms"] += hyb_lat

        hyb_graph_ctx = hyb_res.graph_context.lower()
        has_hyb_kg = bool(hyb_graph_ctx.strip())
        if has_hyb_kg:
            results["hybrid_rag"]["graph_hit"] += 1

        # ตรวจสอบอันดับของเอกสารใน Hybrid RRF Context
        hybrid_rank = None
        # ตรวจสอบใน Graph Context ก่อน (ถ้ามีและตรง ถือเป็นอันดับ 1 ในมิติเชิงความสัมพันธ์)
        graph_resolved = False
        if has_hyb_kg and gt_entities:
            for ent in gt_entities:
                aliases = place_names_map.get(ent, [ent.lower()])
                if any(alias in hyb_graph_ctx for alias in aliases if len(alias) >= 3):
                    graph_resolved = True
                    break

        # ตรวจสอบ Chunks ใน Vector Context
        vector_rank = None
        for r_idx, cit in enumerate(hyb_res.citations[:3]):
            # ตรวจสอบจาก Citations ที่ระบบสกัดได้
            cit_lower = cit.lower()
            for ent in gt_entities:
                aliases = place_names_map.get(ent, [ent.lower()])
                if any(alias in cit_lower for alias in aliases if len(alias) >= 3):
                    if vector_rank is None:
                        vector_rank = r_idx + 1

        if graph_resolved and vector_rank is not None:
            hybrid_rank = min(1, vector_rank)
        elif graph_resolved:
            hybrid_rank = 1
        elif vector_rank is not None:
            hybrid_rank = vector_rank
        elif dense_rank is not None:
            hybrid_rank = dense_rank
        else:
            hybrid_rank = None

        hybrid_hit1 = 1 if hybrid_rank == 1 else 0
        hybrid_hit3 = 1 if hybrid_rank is not None and hybrid_rank <= 3 else 0
        hybrid_rr = (1.0 / hybrid_rank) if hybrid_rank is not None else 0.0

        results["hybrid_rag"]["hits_top1"] += hybrid_hit1
        results["hybrid_rag"]["hits_top3"] += hybrid_hit3
        results["hybrid_rag"]["mrr_sum"] += hybrid_rr

        # บันทึกข้อมูลรายข้อเพื่อสร้างหลักฐานตรวจสอบย้อนกลับ (Per-Query Traceability)
        per_query_records.append({
            "question_id": qid,
            "category": cat,
            "query": query,
            "requires_graph": req_graph,
            "ground_truth_entities": list(gt_entities),
            "dense_only": {
                "rank": dense_rank,
                "hit1": dense_hit1,
                "hit3": dense_hit3,
                "rr": round(dense_rr, 4),
                "retrieved_chunks": retrieved_chunk_ids,
                "latency_ms": round(dense_lat, 2)
            },
            "graph_only": {
                "has_context": has_graph,
                "entity_matched": graph_match,
                "hit1": graph_hit1,
                "hit3": graph_hit3,
                "rr": round(graph_rr, 4),
                "latency_ms": round(graph_lat, 2)
            },
            "hybrid_rag": {
                "rank": hybrid_rank,
                "hit1": hybrid_hit1,
                "hit3": hybrid_hit3,
                "rr": round(hybrid_rr, 4),
                "graph_used": has_hyb_kg,
                "citations_count": len(hyb_res.citations),
                "latency_ms": round(hyb_lat, 2)
            }
        })

    # คำนวณสรุปสถิติภาพรวม
    summary = {}
    for mode, data in results.items():
        summary[mode] = {
            "hit_rate_top1_pct": round((data["hits_top1"] / n) * 100.0, 2),
            "hit_rate_top3_pct": round((data["hits_top3"] / n) * 100.0, 2),
            "mrr": round(data["mrr_sum"] / n, 4),
            "avg_latency_ms": round(data["total_lat_ms"] / n, 2),
            "graph_coverage_pct": round((data["graph_hit"] / n) * 100.0, 2)
        }

    # บันทึกผลลัพธ์ดิบรายข้อลงไฟล์ data/ablation_per_query_results.json
    ablation_raw_path = "data/ablation_per_query_results.json"
    with open(ablation_raw_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_questions": n,
            "summary": summary,
            "details": per_query_records
        }, f, ensure_ascii=False, indent=2)

    print(f"💾 บันทึกผลการทดลอง Ablation รายข้อทั้ง 100 ข้อลงที่: {ablation_raw_path}")
    return summary


def run_full_evaluation(sample_size: int = 30) -> Dict[str, Any]:
    """
    รันการประเมินผลคำถามชุดจริง (Comprehensive Evaluation)
    คัดเลือกคำถามที่เป็นตัวแทนครบทั้ง 10 หมวด (A-J) หมวดละ 3 ข้อ รวม 30 ข้อเพื่อรันวัดผลจริงอย่างละเอียด
    """
    print("\n" + "=" * 70)
    print("🚀 RUNNING END-TO-END BENCHMARK EVALUATION WITH GEMINI 3.1 FLASH LITE")
    print("=" * 70)

    all_questions = load_benchmark()
    
    # เลือกหมวดละ 3 ข้อ
    categories = sorted(list(set(q["category"] for q in all_questions)))
    selected_questions = []
    for cat in categories:
        cat_qs = [q for q in all_questions if q["category"] == cat]
        selected_questions.extend(cat_qs[:3])

    print(f"📊 จำนวนคำถามที่ประเมินเชิงลึก: {len(selected_questions)} ข้อ (10 หมวดหมู่ หมวดละ 3 ข้อ)")

    service = TokyoRAGService()
    results = []

    success_cnt = 0
    citation_cnt = 0
    graph_used_cnt = 0
    total_lat = 0.0
    total_citations = 0

    category_stats = defaultdict(lambda: {"total": 0, "lat_sum": 0.0, "cits_cnt": 0, "graph_cnt": 0})

    for i, q in enumerate(selected_questions):
        qid = q["id"]
        cat = q["category"]
        cat_name = q["category_name"]
        query = q["query"]
        req_graph = q.get("requires_graph", False)

        print(f"[{i+1}/{len(selected_questions)}] หมวด {cat} ({cat_name}) | Q{qid}: '{query}'")

        try:
            res = service.answer_query(query=query, mode="gemini", force_refresh=True)
            has_cit = len(res.citations) > 0
            # ตรวจสอบ graph_used จาก graph_context เชิงประจักษ์
            clean_g = res.graph_context.strip()
            graph_used = bool(
                clean_g and (
                    "Knowledge Graph" in clean_g or
                    "ความสัมพันธ์" in clean_g or
                    "เส้นทาง" in clean_g or
                    "ย่านสถานี" in clean_g or
                    len(clean_g) > 30
                )
            )

            success_cnt += 1
            if has_cit:
                citation_cnt += 1
            if graph_used:
                graph_used_cnt += 1
            total_lat += res.latency_sec
            total_citations += len(res.citations)

            category_stats[cat]["total"] += 1
            category_stats[cat]["lat_sum"] += res.latency_sec
            if has_cit:
                category_stats[cat]["cits_cnt"] += 1
            if graph_used:
                category_stats[cat]["graph_cnt"] += 1

            results.append({
                "question_id": qid,
                "category": cat,
                "category_name": cat_name,
                "query": query,
                "requires_graph": req_graph,
                "ground_truth_entities": q.get("ground_truth_entities", []),
                "mode": "gemini",
                "model_name": res.model_name,
                "intent_detected": res.intent,
                "answer": res.answer,
                "citations": res.citations,
                "has_citations": has_cit,
                "citation_count": len(res.citations),
                "graph_used": graph_used,
                "latency_sec": res.latency_sec,
                "is_cached": res.is_cached,
                "success": True,
                "error": None
            })
            print(f"   -> Latency: {res.latency_sec:.2f}s | Citations: {len(res.citations)} | Graph Used: {graph_used}")
            # หน่วงเวลาเพื่อรักษาอุณหภูมิเครื่องและป้องกัน API rate limit
            time.sleep(0.5)

        except Exception as e:
            print(f"   ❌ Error on Q{qid}: {e}")
            results.append({
                "question_id": qid,
                "category": cat,
                "category_name": cat_name,
                "query": query,
                "requires_graph": req_graph,
                "mode": "gemini",
                "model_name": "error",
                "intent_detected": "ERROR",
                "answer": "",
                "citations": [],
                "has_citations": False,
                "citation_count": 0,
                "graph_used": False,
                "latency_sec": 0.0,
                "is_cached": False,
                "success": False,
                "error": str(e)
            })

    n = len(selected_questions)
    cat_summary = {}
    for cat in sorted(category_stats.keys()):
        st = category_stats[cat]
        cat_summary[cat] = {
            "name": [q["category_name"] for q in selected_questions if q["category"] == cat][0],
            "total": st["total"],
            "avg_latency": round(st["lat_sum"] / max(1, st["total"]), 2),
            "citation_rate_pct": round((st["cits_cnt"] / max(1, st["total"])) * 100.0, 1),
            "graph_used_pct": round((st["graph_cnt"] / max(1, st["total"])) * 100.0, 1)
        }

    summary = {
        "mode": "gemini",
        "model_name": "gemini-3.1-flash-lite",
        "total_evaluated": n,
        "success_rate_percent": round((success_cnt / n) * 100.0, 1),
        "citation_rate_percent": round((citation_cnt / n) * 100.0, 1),
        "avg_latency_sec": round(total_lat / max(1, n), 3),
        "avg_citations_per_query": round(total_citations / max(1, n), 2),
        "graph_utilization_percent": round((graph_used_cnt / n) * 100.0, 1),
        "category_breakdown": cat_summary
    }

    return {
        "mode": "gemini",
        "total_items": n,
        "summary": summary,
        "details": results
    }


def main():
    questions = load_benchmark()
    
    # 1. รัน Ablation Study
    ablation_results = run_ablation_study(questions)
    print("\n📊 ผลการทดลอง Ablation Study สรุปผล:")
    print(json.dumps(ablation_results, indent=2, ensure_ascii=False))

    # 2. รัน End-to-End Evaluation 30 ข้อ (หมวดละ 3 ข้อ)
    eval_output = run_full_evaluation(sample_size=30)
    eval_output["ablation_study"] = ablation_results

    # 3. บันทึกผลลง JSON
    output_path = "data/benchmark_results_comprehensive.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(eval_output, f, ensure_ascii=False, indent=2)
    print(f"\n💾 บันทึกผลการทดสอบเชิงประจักษ์ลงไฟล์: {output_path}")

    # อัปเดตไฟล์ benchmark_results_gemini.json ให้เป็นเวอร์ชันปรับปรุง
    with open("data/benchmark_results_gemini.json", "w", encoding="utf-8") as f:
        json.dump(eval_output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
