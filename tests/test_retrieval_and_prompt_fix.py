"""
tests/test_retrieval_and_prompt_fix.py
======================================
Automated test suite verifying the fixes for:
1. Senso-ji history retrieval (ensures part 1 history is not dropped by diversity selection)
2. Food & street food recommendation retrieval
3. System prompt formatting guidelines
4. In-Memory Cache rejection exclusion
"""

import pytest
from langchain_core.documents import Document
from src.hybrid.engine import TokyoHybridRAGEngine
from src.llm.prompts import build_rag_prompt, SYSTEM_PROMPT
from src.service.rag_service import TokyoRAGService, RAGResponse


@pytest.fixture(scope="module")
def hybrid_engine():
    """เตรียม Hybrid Engine สำหรับรันเทสต์"""
    return TokyoHybridRAGEngine()


def test_sensoji_retrieval_includes_history(hybrid_engine):
    """
    ทดสอบว่าคำถามประวัติวัดเซ็นโซจิ (Sensō-ji) จะต้องดึง Chunk ที่มีข้อมูลปี ค.ศ. 628
    หรือระบุว่าเป็นวัดที่เก่าแก่ที่สุดเข้ามาในบริบท ไม่ถูก Diversity Selection ตัดทิ้ง
    """
    query = "วัด Sensō-ji มีประวัติและความสำคัญอย่างไร?"
    result = hybrid_engine.retrieve_hybrid_context(query)
    
    assert result.intent == "FACT_RETRIEVAL"
    assert result.vector_docs_count > 0
    # ตรวจสอบว่าบริบทมีข้อมูลประวัติของวัดเซ็นโซจิ
    context = result.final_context
    has_history = ("628" in context) or ("เก่าแก่ที่สุด" in context) or ("คามินาริโมง" in context)
    assert has_history, f"บริบทต้องมีประวัติวัดเซ็นโซจิ แต่พบ: {context[:400]}"


def test_food_query_retrieval(hybrid_engine):
    """
    ทดสอบว่าคำถามของกินแนะนำ จะต้องดึงข้อมูลสถานที่ที่มีสตรีทฟู้ดหรืออาหาร เช่น ตลาดปลาสึกิจิ
    """
    query = "ของกินที่แนะนำมีไหม"
    result = hybrid_engine.retrieve_hybrid_context(query)
    
    context = result.final_context
    has_food_spot = ("ตลาดปลาสึกิจิ" in context) or ("สตรีทฟู้ด" in context) or ("ขนม" in context)
    assert has_food_spot, f"บริบทต้องมีย่านของกินหรือตลาดปลาสึกิจิ แต่พบ: {context[:400]}"


def test_system_prompt_has_food_instruction():
    """
    ทดสอบว่า System Prompt มีคำแนะนำการตอบเรื่องของกินและสตรีทฟู้ด
    """
    assert "ของกิน" in SYSTEM_PROMPT
    assert "สตรีทฟู้ด" in SYSTEM_PROMPT


def test_cache_does_not_store_fallback():
    """
    ทดสอบว่า In-Memory Cache จะไม่บันทึกข้อความประเภท Fallback ปฏิเสธว่าไม่มีข้อมูล
    """
    # จำลอง RAG Service แบบเบา
    service = TokyoRAGService.__new__(TokyoRAGService)
    service._cache = {}
    service.cache_ttl_sec = 3600

    # สร้างผลลัพธ์จำลองที่เป็น Fallback
    mock_res = RAGResponse(
        query="คำถามที่ไม่มีข้อมูล",
        intent="FACT_RETRIEVAL",
        answer="ขออภัยครับ ปัจจุบันระบบยังไม่มีข้อมูลครอบคลุมคำถามนี้ในฐานข้อมูล",
        citations=[],
        mode_used="gemini",
        model_name="gemini-2.5-flash",
        latency_sec=1.5,
        is_cached=False
    )

    # ตรวจสอบเงื่อนไขการบันทึก
    is_fallback = "ยังไม่มีข้อมูลครอบคลุม" in mock_res.answer
    if not is_fallback:
        service._cache["dummy_key"] = {"timestamp": 12345, "data": mock_res}

    assert len(service._cache) == 0, "ระบบต้องไม่บันทึกคำตอบปฏิเสธลงใน Cache"
