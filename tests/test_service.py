"""
tests/test_service.py
=====================
Automated Unit & Integration Tests สำหรับ Phase 5: System Integration & RAG Orchestrator
- ทดสอบการทำงานของ TokyoRAGService และ Response Caching
- ทดสอบ End-to-End Query Answering กับ Gemini API
- ทดสอบ Fallback Mechanism เมื่อ Local LLM ออฟไลน์
- ทดสอบ Intent Routing และการประกอบ Context
"""

import os
import pytest
from unittest.mock import MagicMock
from dotenv import load_dotenv

from src.service.rag_service import TokyoRAGService, RAGResponse
from src.hybrid.engine import HybridContextResult
from src.llm.local_llm import LLMResponse

load_dotenv()


def test_rag_service_cache_mechanism():
    """ทดสอบระบบ In-Memory Response Caching เพื่อประหยัดเวลาและพลังงานเครื่อง"""
    # จำลอง Mock Engine และ Gemini Client เพื่อทดสอบ Logic Caching อย่างรวดเร็ว
    mock_engine = MagicMock()
    mock_engine.retrieve_hybrid_context.return_value = HybridContextResult(
        intent="ROUTE_TRANSIT",
        final_context="เส้นทาง Shinjuku ไป Shibuya ใช้ JR Yamanote Line 7 นาที",
        graph_context="Shinjuku -> Shibuya",
        vector_docs_count=1,
        citations=["JR Yamanote Line"]
    )

    service = TokyoRAGService(hybrid_engine=mock_engine)
    service.gemini_client.answer_rag_query = MagicMock(return_value=LLMResponse(
        text="ใช้ JR Yamanote Line ใช้เวลา 7 นาที [อ้างอิง: JR Yamanote Line]",
        model="gemini-test",
        latency_sec=0.01,
        citations=["JR Yamanote Line"],
        success=True,
    ))
    service.clear_cache()

    query = "เดินทางจาก Shinjuku ไป Shibuya ใช้สายอะไร"

    # รอบที่ 1: ดึงข้อมูลจริง (mocked)
    res1 = service.answer_query(query, mode="gemini")
    assert isinstance(res1, RAGResponse)
    assert res1.is_cached is False
    assert mock_engine.retrieve_hybrid_context.call_count == 1

    # รอบที่ 2: ดึงจาก In-Memory Cache (ต้องไม่เรียก engine ซ้ำ)
    res2 = service.answer_query(query, mode="gemini")
    assert isinstance(res2, RAGResponse)
    assert res2.is_cached is True
    assert mock_engine.retrieve_hybrid_context.call_count == 1  # จำนวนครั้งไม่เพิ่มขึ้น

    # ล้างแคชแล้วเรียกใหม่
    service.clear_cache()
    res3 = service.answer_query(query, mode="gemini")
    assert res3.is_cached is False
    assert mock_engine.retrieve_hybrid_context.call_count == 2


def test_rag_service_local_offline_fallback():
    """ทดสอบว่าเมื่อ Local LLM ออฟไลน์ ระบบจะทำการ Fallback อัตโนมัติไม่ทำให้เกิด Error ค้าง"""
    mock_engine = MagicMock()
    mock_engine.retrieve_hybrid_context.return_value = HybridContextResult(
        intent="ROUTE_TRANSIT",
        final_context="ข้อมูลเส้นทางทดสอบ",
        graph_context="A -> B",
        vector_docs_count=1,
        citations=["สถานี A"]
    )

    service = TokyoRAGService(hybrid_engine=mock_engine)
    # จำลองให้ local_client รายงานสถานะ offline
    service.local_client.check_health = MagicMock(return_value={"status": "offline"})

    query = "ทดสอบเส้นทางในโหมด Local LLM"
    res = service.answer_query(query, mode="local")

    assert isinstance(res, RAGResponse)
    # ระบบต้องไม่เกิด Exception และมีคำตอบพร้อมชี้แจงสถานะ Fallback
    assert len(res.answer) > 0
    assert ("สลับมาใช้ Gemini API" in res.answer) or ("Ollama ปิดอยู่" in res.answer) or ("Fallback" in res.model_name)


def test_rag_service_intent_and_citations():
    """ทดสอบการส่งผ่าน Intent และ Citations ใน Service Layer"""
    mock_engine = MagicMock()
    mock_engine.retrieve_hybrid_context.return_value = HybridContextResult(
        intent="ROUTE_TRANSIT",
        final_context="จาก Asakusa ไป Ueno ใช้สาย Ginza Line [อ้างอิง: Ginza Line]",
        graph_context="Asakusa -[Ginza Line]-> Ueno",
        vector_docs_count=1,
        citations=["Ginza Line"]
    )

    service = TokyoRAGService(hybrid_engine=mock_engine)
    # จำลอง gemini_client ให้ตอบพร้อม citation
    mock_gemini = MagicMock()
    mock_gemini.answer_rag_query.return_value = LLMResponse(
        text="คุณสามารถนั่งรถไฟ [อ้างอิง: Ginza Line] ได้โดยตรง",
        citations=["Ginza Line"],
        latency_sec=0.5,
        model="gemini-2.5-flash",
        success=True
    )
    service.gemini_client = mock_gemini

    res = service.answer_query("Asakusa ไป Ueno", mode="gemini")
    assert res.intent == "ROUTE_TRANSIT"
    assert "Ginza Line" in res.citations
    assert res.graph_context == "Asakusa -[Ginza Line]-> Ueno"
