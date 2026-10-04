"""
src/service/rag_service.py
==========================
End-to-End Orchestrator สำหรับระบบ Tokyo Smart Transit & Tourism Hybrid Graph RAG
(Phase 5: System Integration & Error Handling)

หน้าที่หลัก:
1. รับคำถามภาษาไทย/อังกฤษ/ญี่ปุ่น จากผู้ใช้
2. วิเคราะห์และส่งต่อให้ Hybrid RAG Engine (Intent Routing -> Multi-retrieval -> Re-ranking -> Context Assembly)
3. ส่งต่อ Context ให้กับ LLM Backend ที่กำหนด (Gemini API, Local LLM หรือ Side-by-Side Comparator)
4. สกัดคำตอบพร้อมแหล่งอ้างอิง [อ้างอิง: ...] ที่ตรวจสอบย้อนกลับได้ (Traceable Citations)
5. ระบบ In-Memory Response Caching เพื่อประหยัด API Quota และลดภาระการประมวลผลของเครื่อง
6. ระบบ Graceful Fallback ป้องกันระบบล่มเมื่อ Service ใดขาดการเชื่อมต่อ
"""

import os
import time
import hashlib
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

import psutil
from src.hybrid.engine import TokyoHybridRAGEngine, HybridContextResult
from src.llm.gemini_llm import GeminiLLMClient
from src.llm.local_llm import LocalLLMClient, LLMResponse
from src.llm.comparator import LLMComparator, ComparisonResult
from src.llm.prompts import extract_citations

load_dotenv()


class RAGResponse(BaseModel):
    """
    ข้อมูลผลลัพธ์คำตอบปลายทางของระบบ RAG
    """
    query: str = Field(..., description="คำถามต้นฉบับของผู้ใช้")
    intent: str = Field(..., description="เจตนาของคำถาม (ROUTE_TRANSIT, FACT_RETRIEVAL, HYBRID_COMPLEX)")
    answer: str = Field(..., description="ข้อความคำตอบที่สร้างโดย LLM หรือ Fallback")
    citations: List[str] = Field(default_factory=list, description="รายการแหล่งอ้างอิงที่พบในคำตอบ")
    mode_used: str = Field(..., description="โหมดที่ประมวลผล (gemini, local, compare, context_fallback)")
    model_name: str = Field(..., description="ชื่อโมเดล AI ที่ใช้สร้างคำตอบ")
    latency_sec: float = Field(0.0, description="เวลาประมวลผลรวมทั้งหมด (วินาที)")
    is_cached: bool = Field(False, description="ผลลัพธ์นี้มาจาก Memory Cache หรือไม่")
    graph_context: str = Field("", description="บริบทเส้นทางหรือความสัมพันธ์จาก Knowledge Graph")
    comparison: Optional[ComparisonResult] = Field(None, description="ผลการเปรียบเทียบกรณีรันในโหมด compare")
    prompt_tokens: int = Field(0, description="จำนวน Token ของ Prompt")
    completion_tokens: int = Field(0, description="จำนวน Token ของคำตอบ")
    total_tokens: int = Field(0, description="จำนวน Token รวมทั้งหมด")
    tokens_per_sec: float = Field(0.0, description="ความเร็วสร้างคำตอบ (Tokens/วินาที)")
    ram_usage_mb: float = Field(0.0, description="ขนาด RAM ของ Process ปัจจุบัน (MB)")
    ram_percent: float = Field(0.0, description="การใช้ RAM ทั้งหมดของระบบ (%)")


class TokyoRAGService:
    """
    End-to-End RAG Service Orchestrator
    บูรณาการทุกส่วนของระบบและจัดการ Error Handling & Resource Throttling
    """

    def __init__(
        self,
        hybrid_engine: Optional[TokyoHybridRAGEngine] = None,
        default_gemini_model: str = "gemini-2.5-flash",
        default_local_model: str = "qwen2.5:3b",
        cache_ttl_sec: int = 3600
    ):
        """
        เริ่มต้นการทำงานของ Service Layer
        """
        print("[TokyoRAGService] กำลังเริ่มต้นระบบ RAG Orchestrator...")
        
        # 1. เชื่อมต่อ Hybrid Retrieval Engine
        if hybrid_engine is not None:
            self.engine = hybrid_engine
        else:
            self.engine = TokyoHybridRAGEngine()

        # 2. เตรียม LLM Clients
        self.default_gemini_model = os.getenv("GEMINI_MODEL", default_gemini_model)
        self.default_local_model = os.getenv("LOCAL_LLM_MODEL", default_local_model)

        self.gemini_client = GeminiLLMClient(model_name=self.default_gemini_model)
        self.local_client = LocalLLMClient(model_name=self.default_local_model)
        self.comparator = LLMComparator(
            local_model=self.default_local_model,
            gemini_model=self.default_gemini_model
        )

        # 3. Memory Cache สำหรับจัดเก็บคำตอบ
        self.cache_ttl_sec = cache_ttl_sec
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _generate_cache_key(self, query: str, mode: str) -> str:
        """สร้างคีย์แคชที่ไม่ซ้ำจากคำถามและโหมดที่เลือก"""
        normalized = f"{mode.lower()}::{query.strip().lower()}"
        return hashlib.md5(normalized.encode("utf-8")).hexdigest()

    def clear_cache(self) -> None:
        """ล้าง Response Cache ในหน่วยความจำ"""
        self._cache.clear()
        print("[TokyoRAGService] ล้าง Response Cache เรียบร้อยแล้ว")

    @staticmethod
    def _ensure_retrieval_citations(
        answer: str,
        generated_citations: List[str],
        retrieved_citations: List[str],
    ) -> tuple[str, List[str]]:
        """Attach traceable retrieval sources when an LLM omitted citation tags."""
        if generated_citations or not retrieved_citations:
            return answer, generated_citations
        grounded = list(dict.fromkeys(retrieved_citations))[:3]
        citation_line = " ".join(f"[อ้างอิง: {source}]" for source in grounded)
        return f"{answer.rstrip()}\n\n📚 ข้อมูลอ้างอิงยืนยัน: {citation_line}", grounded

    def _format_offline_fallback(self, query: str, context: str, graph_context: str) -> str:
        """
        จัดรูปแบบข้อความตอบกลับในโหมด Offline Fallback ให้สวยงาม ไพเราะ และเป็นภาษาไทยล้วน (ตัดข้อความภาษาอังกฤษออก)
        """
        import re
        output_sections = []
        output_sections.append("ขอสรุปข้อมูลการเดินทางและสถานที่ท่องเที่ยวในโตเกียวตามที่สอบถาม ดังนี้ครับ:")

        # 1. ข้อมูลเส้นทางรถไฟ (ถ้ามี)
        if graph_context.strip():
            clean_graph = graph_context.replace("[ข้อมูลเส้นทางรถไฟจาก Knowledge Graph]:", "").strip()
            output_sections.append(f"🚆 แผนการเดินทางและเส้นทางรถไฟ:\n{clean_graph}")

        # 2. ข้อมูลสถานที่ท่องเที่ยว (สกัดเฉพาะภาษาไทย)
        blocks = re.findall(r"\[ข้อมูลที่ \d+ \| อ้างอิง: ([^\]]+)\]\s*\n(.*?)(?=\[ข้อมูลที่|\Z)", context, re.DOTALL)
        if blocks:
            place_list = []
            seen = set()
            for title, body in blocks:
                clean_name = re.sub(r"\(.*?\)", "", title).split("-")[0].strip()
                if clean_name in seen:
                    continue
                seen.add(clean_name)

                # ดึงเฉพาะประโยคภาษาไทย
                thai_lines = [
                    line.strip() for line in body.split("\n")
                    if any('\u0e00' <= char <= '\u0e7f' for char in line) and not line.strip().startswith("Visiting")
                ]
                desc = " ".join(thai_lines[:2]).strip()
                if desc:
                    place_list.append(f"📍 {clean_name}\n   • {desc}")

            if place_list:
                output_sections.append("🗺️ สถานที่ท่องเที่ยวที่เกี่ยวข้อง:\n" + "\n\n".join(place_list))

        return "\n\n".join(output_sections) if len(output_sections) > 1 else "ขออภัยครับ ข้อมูลในระบบยังไม่ครอบคลุมคำถามนี้อย่างสมบูรณ์"

    def answer_query(
        self,
        query: str,
        mode: str = "gemini",
        force_refresh: bool = False
    ) -> RAGResponse:
        """
        ฟังก์ชันหลักในการตอบคำถาม:
        1. ตรวจสอบ Cache ก่อน เพื่อประหยัดแรงเครื่องและ API
        2. ดึงข้อมูลบริบทผ่าน Hybrid Engine (Graph + Vector + BM25)
        3. ประมวลผลคำตอบตามโหมดที่เลือก:
           - 'gemini': ใช้ Google Gemini API (คลาวด์ ไม่กินทรัพยากรเครื่อง)
           - 'local': ใช้ Ollama Local LLM (คัดกรอง 3B/4B พร้อม Fallback)
           - 'compare': ทดสอบเปรียบเทียบทั้งสองโมเดลพร้อมกัน Side-by-Side
        """
        start_time = time.time()
        cache_key = self._generate_cache_key(query, mode)

        # 1. ตรวจสอบ In-Memory Cache
        if not force_refresh and cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            # ตรวจสอบอายุ TTL
            if (time.time() - cache_entry["timestamp"]) < self.cache_ttl_sec:
                cached_res: RAGResponse = cache_entry["data"].model_copy(deep=True)
                cached_res.is_cached = True
                cached_res.latency_sec = round(time.time() - start_time, 4)
                return cached_res

        # 2. ดึงข้อมูลผ่าน Hybrid RAG Engine
        hybrid_res: HybridContextResult = self.engine.retrieve_hybrid_context(query)
        context = hybrid_res.final_context
        intent = hybrid_res.intent
        graph_ctx = hybrid_res.graph_context

        # 3. ส่งต่อ LLM ตาม Mode
        clean_mode = mode.lower().strip()

        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        tokens_per_sec = 0.0

        # --- MODE 1: Google Gemini API (Recommended / Zero Machine Overhead) ---
        if clean_mode == "gemini":
            gemini_resp = self.gemini_client.answer_rag_query(query, context)
            if gemini_resp.success:
                answer = gemini_resp.text
                citations = gemini_resp.citations or extract_citations(answer)
                answer, citations = self._ensure_retrieval_citations(
                    answer, citations, hybrid_res.citations
                )
                model_used = gemini_resp.model
                mode_used = "gemini"
                prompt_tokens = gemini_resp.prompt_tokens
                completion_tokens = gemini_resp.completion_tokens
                total_tokens = gemini_resp.total_tokens
                tokens_per_sec = gemini_resp.tokens_per_sec
            else:
                # Fallback: หาก API ติดขัด ให้สังเคราะห์คำตอบภาษาไทยจาก Graph และ Vector โดยตัดภาษาอังกฤษออก
                citations = hybrid_res.citations or extract_citations(context)
                answer = self._format_offline_fallback(query, context, graph_ctx)
                model_used = "Tokyo-Hybrid-Retriever (Offline)"
                mode_used = "context_fallback"
                prompt_tokens = len(context) // 4
                completion_tokens = len(answer) // 4
                total_tokens = prompt_tokens + completion_tokens

            # วัดการใช้งาน RAM ของ Process ปัจจุบันและระบบ
            try:
                proc = psutil.Process()
                ram_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
                ram_pct = round(psutil.virtual_memory().percent, 1)
            except Exception:
                ram_mb = 0.0
                ram_pct = 0.0

            total_lat = round(time.time() - start_time, 3)
            result = RAGResponse(
                query=query,
                intent=intent,
                answer=answer,
                citations=citations,
                mode_used=mode_used,
                model_name=model_used,
                latency_sec=total_lat,
                is_cached=False,
                graph_context=graph_ctx,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                tokens_per_sec=tokens_per_sec,
                ram_usage_mb=ram_mb,
                ram_percent=ram_pct
            )

        # --- MODE 2: Local LLM (Ollama 3B/4B Safe Throttling) ---
        elif clean_mode == "local":
            # ตรวจสอบความพร้อมของ Local Ollama ก่อนรันจริงเพื่อป้องกันการค้าง
            health = self.local_client.check_health()
            if health.get("status") != "online":
                # หาก Ollama ไม่ได้เปิดอยู่ ให้แจ้งเตือนพร้อมสลับใช้ Gemini หรือ Context Fallback
                if os.getenv("GEMINI_API_KEY"):
                    gemini_fallback = self.gemini_client.answer_rag_query(query, context)
                    answer = (
                        f"ℹ️ (Local LLM ไม่ได้รันอยู่ — สลับมาใช้ Gemini API สำรองอัตโนมัติ)\n\n"
                        f"{gemini_fallback.text}"
                    )
                    citations = gemini_fallback.citations or extract_citations(answer)
                    answer, citations = self._ensure_retrieval_citations(
                        answer, citations, hybrid_res.citations
                    )
                    model_used = f"{gemini_fallback.model} (Auto-fallback)"
                    mode_used = "gemini"
                    prompt_tokens = gemini_fallback.prompt_tokens
                    completion_tokens = gemini_fallback.completion_tokens
                    total_tokens = gemini_fallback.total_tokens
                    tokens_per_sec = gemini_fallback.tokens_per_sec
                else:
                    answer = (
                        f"⚠️ (Ollama ปิดอยู่และไม่มี Gemini API Key)\n\n"
                        f"ข้อมูลอ้างอิงจากระบบ:\n{context}"
                    )
                    citations = hybrid_res.citations
                    model_used = "fallback-retrieval"
                    mode_used = "context_fallback"
                    prompt_tokens = len(context) // 4
                    completion_tokens = len(answer) // 4
                    total_tokens = prompt_tokens + completion_tokens
            else:
                local_resp = self.local_client.answer_rag_query(query, context)
                if local_resp.success:
                    answer = local_resp.text
                    citations = local_resp.citations or extract_citations(answer)
                    answer, citations = self._ensure_retrieval_citations(
                        answer, citations, hybrid_res.citations
                    )
                    model_used = local_resp.model
                    mode_used = "local"
                    prompt_tokens = local_resp.prompt_tokens
                    completion_tokens = local_resp.completion_tokens
                    total_tokens = local_resp.total_tokens
                    tokens_per_sec = local_resp.tokens_per_sec
                else:
                    answer = f"⚠️ เกิดข้อผิดพลาดในการประมวลผล Local LLM: {local_resp.error}\n\n{context}"
                    citations = hybrid_res.citations
                    model_used = "fallback-retrieval"
                    mode_used = "context_fallback"

            try:
                proc = psutil.Process()
                ram_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
                ram_pct = round(psutil.virtual_memory().percent, 1)
            except Exception:
                ram_mb = 0.0
                ram_pct = 0.0

            total_lat = round(time.time() - start_time, 3)
            result = RAGResponse(
                query=query,
                intent=intent,
                answer=answer,
                citations=citations,
                mode_used=mode_used,
                model_name=model_used,
                latency_sec=total_lat,
                is_cached=False,
                graph_context=graph_ctx,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                tokens_per_sec=tokens_per_sec,
                ram_usage_mb=ram_mb,
                ram_percent=ram_pct
            )

        # --- MODE 3: Side-by-Side Comparison ---
        elif clean_mode == "compare":
            comp_result: ComparisonResult = self.comparator.compare_rag_answer(query, context)
            total_lat = round(time.time() - start_time, 3)

            # สร้างบทสรุปของทั้งสองโมเดล
            combined_summary = (
                f"### ผลการเปรียบเทียบ Side-by-Side\n\n"
                f"{comp_result.to_markdown_table()}\n\n"
                f"#### คำตอบจาก Gemini ({comp_result.gemini_result.model}):\n"
                f"{comp_result.gemini_result.text}\n\n"
                f"#### คำตอบจาก Local LLM ({comp_result.local_result.model}):\n"
                f"{comp_result.local_result.text}"
            )

            all_citations = list(set(
                (comp_result.gemini_result.citations or []) + 
                (comp_result.local_result.citations or [])
            ))

            result = RAGResponse(
                query=query,
                intent=intent,
                answer=combined_summary,
                citations=all_citations,
                mode_used="compare",
                model_name=f"{comp_result.gemini_result.model} vs {comp_result.local_result.model}",
                latency_sec=total_lat,
                is_cached=False,
                graph_context=graph_ctx,
                comparison=comp_result
            )
        else:
            raise ValueError(f"โหมดไม่ถูกต้อง: {mode} (เลือกได้: 'gemini', 'local', 'compare')")

        # บันทึกลง Memory Cache เฉพาะคำตอบที่มีข้อมูลสมบูรณ์ (ไม่บันทึกกรณีปฏิเสธว่าไม่มีข้อมูล)
        is_fallback_reject = "ยังไม่มีข้อมูลครอบคลุม" in result.answer or "ไม่ครอบคลุมคำถามนี้อย่างสมบูรณ์" in result.answer
        if not is_fallback_reject:
            self._cache[cache_key] = {
                "timestamp": time.time(),
                "data": result
            }

        return result
