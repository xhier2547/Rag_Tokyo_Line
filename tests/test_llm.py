"""
tests/test_llm.py
=================
Automated Unit & Integration Tests สำหรับ Phase 4: Local LLM (3B/4B) และ Gemini API
- ทดสอบการสร้าง Prompt และการดึงข้อมูลการอ้างอิง (Citations)
- ทดสอบการเชื่อมต่อและการตอบสนองของ Local LLM (Ollama 3B/4B)
- ทดสอบการเชื่อมต่อและการตอบสนองของ Google Gemini API
- ทดสอบระบบเปรียบเทียบ Side-by-Side Comparator
"""

import os
import pytest
from dotenv import load_dotenv

from src.llm.prompts import build_rag_prompt, extract_citations, SYSTEM_PROMPT
from src.llm.local_llm import LocalLLMClient, LLMResponse, ALLOWED_3B_4B_MODELS
from src.llm.gemini_llm import GeminiLLMClient
from src.llm.comparator import LLMComparator, ComparisonResult

load_dotenv()


def test_system_prompt_and_builder():
    """ทดสอบการประกอบ Prompt และตรวจสอบ Zero-Hallucination กฎเหล็ก"""
    assert "Zero-Hallucination" in SYSTEM_PROMPT or "กฎเหล็ก" in SYSTEM_PROMPT
    assert "[อ้างอิง:" in SYSTEM_PROMPT
    
    query = "เดินทางจากชินจูกุไปชิบูย่ายังไง"
    context = "สถานี Shinjuku เชื่อมต่อกับสถานี Shibuya ด้วยสาย JR Yamanote Line ใช้เวลา 7 นาที"
    prompt = build_rag_prompt(query, context)
    
    assert query in prompt
    assert context in prompt
    assert "บริบทอ้างอิง" in prompt


def test_citation_extraction():
    """ทดสอบฟังก์ชันสกัดเครื่องหมายอ้างอิง [อ้างอิง: ...]"""
    sample_text = (
        "คุณสามารถนั่งรถไฟ [อ้างอิง: JR Yamanote Line] จากสถานี [อ้างอิง: สถานี Shinjuku] "
        "ไปยังสถานี [อ้างอิง: สถานี Shibuya] ใช้เวลาประมาณ 7 นาที"
    )
    citations = extract_citations(sample_text)
    assert len(citations) == 3
    assert "JR Yamanote Line" in citations
    assert "สถานี Shinjuku" in citations
    assert "สถานี Shibuya" in citations


def test_local_llm_health_and_3b_4b_filter():
    """ทดสอบ Health check ของ Ollama และการคัดกรองโมเดลขนาด 3B-4B"""
    client = LocalLLMClient(model_name="qwen2.5:3b")
    health = client.check_health()
    
    if health.get("status") == "online":
        assert "available_3b_4b_models" in health
        # ตรวจสอบว่ามีโมเดล 3b หรือ 4b ติดตั้งอยู่ในเครื่อง
        assert len(health["available_3b_4b_models"]) > 0
        # ตรวจสอบโมเดลที่แนะนำ
        assert any("3b" in m or "4b" in m for m in health["available_3b_4b_models"])


def test_local_llm_generation_3b():
    """ทดสอบการสร้างคำตอบด้วย Local LLM ขนาด 3B (qwen2.5:3b)"""
    client = LocalLLMClient(model_name="qwen2.5:3b")
    health = client.check_health()
    if health.get("status") != "online":
        pytest.skip("Ollama is not running locally")
        
    query = "เดินทางจากสถานี Asakusa ไปสถานี Ueno ใช้สายอะไรและกี่นาที?"
    context = "เส้นทาง: สถานี Asakusa เชื่อมต่อไปยังสถานี Ueno ผ่านสาย Ginza Line ใช้เวลา 5 นาที [อ้างอิง: Ginza Line]"
    
    res = client.answer_rag_query(query, context)
    assert isinstance(res, LLMResponse)
    assert res.success is True
    assert res.latency_sec > 0
    assert len(res.text) > 0
    assert res.prompt_tokens > 0 or res.total_tokens > 0


def test_gemini_llm_generation():
    """ทดสอบการสร้างคำตอบด้วย Google Gemini API (gemini-2.5-flash)"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY is not set in .env")
        
    client = GeminiLLMClient(model_name="gemini-2.5-flash")
    health = client.check_health()
    if not health.get("healthy"):
        pytest.skip(f"Gemini API is not accessible: {health.get('error')}")
        
    query = "วัดเซ็นโซจิตั้งอยู่ที่ไหนและใกล้สถานีอะไร?"
    context = "วัดเซ็นโซจิ (Senso-ji Temple) ตั้งอยู่ในย่าน Asakusa ใกล้สถานี Asakusa เดิน 5 นาที [อ้างอิง: วัดเซ็นโซจิ]"
    
    res = client.answer_rag_query(query, context)
    assert isinstance(res, LLMResponse)
    assert res.success is True
    assert res.latency_sec > 0
    assert len(res.text) > 0
    assert res.model == "gemini-2.5-flash"


def test_llm_comparator_execution():
    """ทดสอบ Side-by-Side LLM Comparator และการสร้างรายงาน Markdown"""
    api_key = os.getenv("GEMINI_API_KEY")
    comparator = LLMComparator(local_model="qwen2.5:3b", gemini_model="gemini-2.5-flash")
    
    # ทดสอบสุขภาพทั้งสองฝั่ง
    local_online = comparator.local_client.check_health().get("status") == "online"
    if not (local_online and api_key):
        pytest.skip("Either Ollama or Gemini API is not available for comparison")
        
    query = "จาก Shinjuku ไป Shibuya ใช้เวลาเดินทางกี่นาที?"
    context = "สถานี Shinjuku เชื่อมต่อกับสถานี Shibuya โดยสาย JR Yamanote Line ระยะเวลา 7 นาที [อ้างอิง: JR Yamanote Line]"
    
    result = comparator.compare_rag_answer(query, context)
    assert isinstance(result, ComparisonResult)
    assert result.local_result.success is True
    assert result.gemini_result.success is True
    
    # ตรวจสอบการสร้างตารางสรุปผล
    md = result.to_markdown_table()
    assert "| **เวลาตอบสนอง (Latency)** |" in md
    assert "qwen2.5:3b" in md
    assert "gemini-2.5-flash" in md
