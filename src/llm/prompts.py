"""
src/llm/prompts.py
===================
โมดูลจัดการ System Prompt และ Prompt Templates สำหรับ Tokyo Hybrid Graph RAG
- รองรับทั้ง Local LLM (Ollama 3B/4B) และ API LLM (Google Gemini)
- กำหนด Zero-Hallucination Guardrail อย่างเข้มงวดตามเกณฑ์ Rubric Level 5
- บังคับการอ้างอิงแหล่งที่มา [อ้างอิง: ...] ทุกครั้งที่ให้ข้อมูล
"""

import re
from typing import List, Dict, Any, Optional

# System Prompt สำหรับ AI ผู้เชี่ยวชาญการท่องเที่ยวและการเดินทางในโตเกียว
SYSTEM_PROMPT = """คุณคือ "Tokyo Transit & Travel AI Assistant" ผู้ช่วยอัจฉริยะด้านการเดินทางและท่องเที่ยวในกรุงโตเกียว ประเทศญี่ปุ่น
หน้าที่ของคุณคือตอบคำถาม วางแผนเส้นทางรถไฟ และแนะนำสถานที่ท่องเที่ยว โดยยึดหลักเกณฑ์ความถูกต้องสูงสุด (Zero-Hallucination)

=== กฎเหล็กในการตอบคำถาม (STRICT RULES) ===
1. ยึดข้อมูลจาก "บริบทอ้างอิง (Context)" ที่ได้รับเท่านั้น ห้ามคาดเดา คิดค้นชื่อสถานี สายรถไฟ เวลาเดินทาง หรือข้อมูลสถานที่เองโดยเด็ดขาด
2. ทุกครั้งที่กล่าวถึงสถานที่, สถานี, สายรถไฟ, หรือระยะเวลาเดินทาง ต้องใส่เครื่องหมายอ้างอิงท้ายข้อความ เช่น [อ้างอิง: วัดเซ็นโซจิ], [อ้างอิง: Ginza Line], [อ้างอิง: สถานี Shinjuku]
3. หากบริบทที่ได้รับ "ไม่มีข้อมูล" หรือ "ไม่เพียงพอ" ที่จะตอบคำถาม ให้แจ้งผู้ใช้อย่างตรงไปตรงมาว่า "ขออภัย ข้อมูลในฐานข้อมูลปัจจุบันยังไม่ครอบคลุมคำถามนี้" และห้ามแต่งข้อมูลขึ้นมาเอง
4. การตอบคำถามเกี่ยวกับเส้นทาง:
   - ระบุสถานีต้นทาง $\\rightarrow$ สายรถไฟ $\\rightarrow$ สถานีปลายทาง
   - ระบุระยะเวลาโดยประมาณ (ถ้ามีในบริบท)
   - หากต้องเดินเท้าไปยังสถานที่ปลายทาง ให้ระบุเวลาเดินเท้าด้วย
5. ใช้ภาษาไทยที่สุภาพ กระชับ อ่านเข้าใจง่าย เป็นมืออาชีพ และจัดลำดับด้วยหัวข้อย่อย (Bullet points) ชัดเจน
"""

PROMPT_TEMPLATE = """{system_prompt}

=== บริบทอ้างอิง (Retrieved Context) ===
{context}

=== คำถามของผู้ใช้ ===
{query}

=== คำตอบของคุณ (ยึดตามบริบทและใส่ [อ้างอิง: ...] ให้ครบถ้วน): ===
"""


def build_rag_prompt(query: str, context: str, system_prompt: Optional[str] = None) -> str:
    """
    สร้าง Full Prompt สำหรับส่งให้ LLM (ทั้ง Ollama 3B/4B และ Gemini)
    
    Args:
        query: คำถามของผู้ใช้
        context: บริบทที่ดึงมาจาก Graph RAG และ Hybrid Vector/BM25
        system_prompt: System prompt ที่กำหนด (ถ้าไม่ใส่จะใช้ค่าเริ่มต้น)
        
    Returns:
        str: ข้อความ Prompt ที่สมบูรณ์
    """
    sys_prompt = system_prompt or SYSTEM_PROMPT
    clean_context = context.strip() if context and context.strip() else "ไม่มีข้อมูลในฐานข้อมูลสำหรับคำถามนี้"
    
    return PROMPT_TEMPLATE.format(
        system_prompt=sys_prompt,
        context=clean_context,
        query=query.strip()
    )


def extract_citations(text: str) -> List[str]:
    """
    สกัดรายการอ้างอิง [อ้างอิง: ...] จากคำตอบของ LLM เพื่อตรวจสอบความถูกต้อง (Verification)
    
    Args:
        text: ข้อความคำตอบจาก LLM
        
    Returns:
        List[str]: รายการชื่อแหล่งอ้างอิงที่พบ
    """
    pattern = r"\[อ้างอิง:\s*([^\]]+)\]"
    matches = re.findall(pattern, text)
    return [m.strip() for m in matches if m.strip()]
