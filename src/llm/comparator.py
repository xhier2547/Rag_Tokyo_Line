"""
src/llm/comparator.py
======================
โมดูลเปรียบเทียบผลลัพธ์ระหว่าง Local LLM (Ollama 3B/4B) และ API LLM (Google Gemini)
- เปรียบเทียบ Latency (เวลาตอบสนอง), Token Throughput (Tokens/sec), และ Citation Verification
- สร้างตารางสรุปผลการเปรียบเทียบในรูปแบบ Markdown และ Dict เพื่อใช้ในบทวิเคราะห์ Rubric Level 5
"""

import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from src.llm.local_llm import LocalLLMClient, LLMResponse
from src.llm.gemini_llm import GeminiLLMClient
from src.llm.prompts import build_rag_prompt

logger = logging.getLogger(__name__)


@dataclass
class ComparisonResult:
    """โครงสร้างข้อมูลเปรียบเทียบผลลัพธ์ระหว่าง 2 โมเดล"""
    query: str
    local_model_name: str
    gemini_model_name: str
    local_result: LLMResponse
    gemini_result: LLMResponse
    latency_difference_sec: float
    faster_model: str

    def to_markdown_table(self) -> str:
        """แปลงผลลัพธ์เป็นตาราง Markdown สำหรับใช้ในรายงานสรุปผล"""
        loc = self.local_result
        gem = self.gemini_result
        
        md = []
        md.append(f"### ผลการทดสอบเปรียบเทียบ LLM สำหรับคำถาม: \"{self.query}\"")
        md.append("")
        md.append("| ตัวชี้วัด (Metric) | Local LLM (Ollama) | API LLM (Google Gemini) | ส่วนต่าง / ข้อสังเกต |")
        md.append("| :--- | :--- | :--- | :--- |")
        md.append(f"| **ชื่อโมเดล** | `{self.local_model_name}` (3B/4B) | `{self.gemini_model_name}` | - |")
        md.append(f"| **เวลาตอบสนอง (Latency)** | **{loc.latency_sec:.2f} วินาที** | **{gem.latency_sec:.2f} วินาที** | {self.faster_model} เร็วกว่า ({abs(self.latency_difference_sec):.2f}s) |")
        md.append(f"| **Output Tokens** | {loc.completion_tokens} tokens | {gem.completion_tokens} tokens | - |")
        md.append(f"| **ความเร็ว (Tokens/sec)** | {loc.tokens_per_sec:.1f} tps | {gem.tokens_per_sec:.1f} tps | - |")
        md.append(f"| **การอ้างอิงที่พบ ([อ้างอิง: ...])** | {len(loc.citations)} รายการ | {len(gem.citations)} รายการ | - |")
        md.append(f"| **สถานะการทำงาน** | {'✅ สำเร็จ' if loc.success else '❌ ผิดพลาด'} | {'✅ สำเร็จ' if gem.success else '❌ ผิดพลาด'} | - |")
        md.append("")
        md.append("#### 📝 คำตอบจาก Local LLM (Ollama 3B/4B):")
        md.append(f"> {loc.text.replace(chr(10), chr(10) + '> ')}")
        md.append("")
        md.append("#### 📝 คำตอบจาก Google Gemini API:")
        md.append(f"> {gem.text.replace(chr(10), chr(10) + '> ')}")
        md.append("")
        return "\n".join(md)


class LLMComparator:
    """
    เครื่องมือเปรียบเทียบการทำงานของ Local LLM และ API LLM
    """

    def __init__(
        self,
        local_model: Optional[str] = None,
        gemini_model: Optional[str] = None
    ):
        """
        เริ่มต้น LLMComparator
        
        Args:
            local_model: ชื่อโมเดล Local Ollama (จำกัด 3B-4B เช่น qwen2.5:3b, gemma3:4b, typhoon2.1-gemma3-4b)
            gemini_model: ชื่อโมเดล Gemini (เช่น gemini-2.5-flash)
        """
        self.local_client = LocalLLMClient(model_name=local_model)
        self.gemini_client = GeminiLLMClient(model_name=gemini_model)

    def compare_rag_answer(
        self,
        query: str,
        context: str,
        temperature: float = 0.2
    ) -> ComparisonResult:
        """
        ส่งคำถามและบริบทเดียวกันให้ทั้ง 2 โมเดล แล้วเปรียบเทียบผลลัพธ์
        
        Args:
            query: คำถามของผู้ใช้
            context: บริบทข้อมูลจาก Hybrid Graph RAG
            temperature: ค่าความหลากหลาย
            
        Returns:
            ComparisonResult: ออบเจกต์สรุปผลการเปรียบเทียบ
        """
        logger.info(f"[LLMComparator] กำลังทดสอบ Local LLM ({self.local_client.model_name})...")
        local_res = self.local_client.answer_rag_query(query, context, temperature=temperature)
        
        logger.info(f"[LLMComparator] กำลังทดสอบ Gemini API ({self.gemini_client.model_name})...")
        gemini_res = self.gemini_client.answer_rag_query(query, context, temperature=temperature)

        lat_diff = round(local_res.latency_sec - gemini_res.latency_sec, 3)
        if local_res.latency_sec < gemini_res.latency_sec:
            faster = f"Local LLM ({self.local_client.model_name})"
        else:
            faster = f"Gemini API ({self.gemini_client.model_name})"

        return ComparisonResult(
            query=query,
            local_model_name=self.local_client.model_name,
            gemini_model_name=self.gemini_client.model_name,
            local_result=local_res,
            gemini_result=gemini_res,
            latency_difference_sec=lat_diff,
            faster_model=faster
        )


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    
    print("=" * 65)
    print("  Tokyo Hybrid Graph RAG: LLM Comparison Benchmark (Phase 4)")
    print("  Comparing Local 3B/4B LLM vs Google Gemini API")
    print("=" * 65)

    sample_query = "เดินทางจากสถานี Asakusa ไปยัง Tokyo Skytree ใช้สายรถไฟอะไร และใช้เวลากี่นาที?"
    sample_context = (
        "1. ข้อมูลเส้นทางรถไฟ (Knowledge Graph):\n"
        "   - สถานีต้นทาง: Asakusa (G19/A18)\n"
        "   - สถานีปลายทาง: Oshiage (SKYTREE) (Z14/A20)\n"
        "   - สายรถไฟ: Toei Asakusa Line\n"
        "   - ระยะเวลาเดินทาง: 3 นาที [อ้างอิง: Toei Asakusa Line]\n"
        "2. ข้อมูลสถานที่ท่องเที่ยว (Vector & BM25):\n"
        "   - โตเกียวสกายทรี (Tokyo Skytree) เป็นหอส่งสัญญาณโทรทัศน์ที่สูงที่สุดในโลก (634 เมตร)\n"
        "   - จากสถานี Oshiage เดินเท้าเชื่อมต่อเข้าตัวอาคาร Tokyo Solamachi ได้ทันที (1 นาที) [อ้างอิง: Tokyo Skytree]"
    )

    comparator = LLMComparator(local_model="qwen2.5:3b", gemini_model="gemini-2.5-flash")
    print(f"\n[Status] Local LLM Model: {comparator.local_client.model_name} (3B/4B constrained)")
    print(f"[Status] API LLM Model:   {comparator.gemini_client.model_name}")
    print("\nRunning comparison query...")
    
    result = comparator.compare_rag_answer(sample_query, sample_context)
    print("\n" + result.to_markdown_table())
