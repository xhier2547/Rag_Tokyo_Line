"""
src/llm/gemini_llm.py
=====================
โมดูลเชื่อมต่อ Google Gemini API สำหรับ Tokyo Hybrid Graph RAG
- รองรับโมเดล gemini-2.5-flash ตามที่ระบุใน .env
- บันทึกเมตริกวัดผล Latency, Token Usage (Prompt & Candidates) และ Tokens/sec
- มีการจัดการข้อผิดพลาด (Rate Limit, Invalid API Key, Network Error) และ Fallback
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from src.llm.local_llm import LLMResponse
from src.llm.prompts import SYSTEM_PROMPT, build_rag_prompt, extract_citations

load_dotenv()
logger = logging.getLogger(__name__)


class GeminiLLMClient:
    """
    Client สำหรับเชื่อมต่อ Google Gemini API
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        เริ่มต้น GeminiLLMClient
        
        Args:
            api_key: Google Gemini API Key (ค่าเริ่มต้นอ่านจาก GEMINI_API_KEY ใน .env)
            model_name: ชื่อโมเดล Gemini (ค่าเริ่มต้นอ่านจาก GEMINI_MODEL ใน .env หรือ gemini-2.5-flash)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._client = None
        self._init_client()

    def _init_client(self) -> None:
        """เตรียม Client เชื่อมต่อผ่าน google-genai SDK"""
        if not self.api_key:
            logger.warning("[GeminiLLM] ไม่พบ GEMINI_API_KEY ใน Environment ตัวแปร")
            return

        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        except Exception as e:
            logger.error(f"[GeminiLLM] เกิดข้อผิดพลาดในการโหลด google.genai: {e}")
            self._client = None

    def check_health(self) -> Dict[str, Any]:
        """
        ตรวจสอบสถานะการเชื่อมต่อ Google Gemini API
        """
        if not self.api_key:
            return {"status": "unconfigured", "error": "GEMINI_API_KEY is not set"}
        
        if self._client is None:
            return {"status": "error", "error": "Client could not be initialized"}

        try:
            start = time.time()
            res = self._client.models.generate_content(
                model=self.model_name,
                contents="ping"
            )
            lat = time.time() - start
            return {
                "status": "online",
                "model": self.model_name,
                "latency_sec": round(lat, 3),
                "healthy": True
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "healthy": False}

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024
    ) -> LLMResponse:
        """
        ส่ง Prompt ให้ Gemini API สร้างคำตอบ
        
        Args:
            prompt: ข้อความคำถามหรือ Full Prompt
            system_prompt: System prompt สำหรับกำหนดบทบาทและเงื่อนไข
            temperature: ความหลากหลายของคำตอบ (0.0-1.0)
            max_tokens: ขีดจำกัดจำนวน Token ที่ตอบ
            
        Returns:
            LLMResponse: ผลลัพธ์พร้อมเวลาและสถิติ Token
        """
        if not self.api_key or self._client is None:
            return LLMResponse(
                text="[ระบบแจ้งเตือน] ไม่พบคีย์ GEMINI_API_KEY ในระบบ กรุณาตรวจสอบไฟล์ .env",
                model=self.model_name,
                latency_sec=0.0,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                tokens_per_sec=0.0,
                citations=[],
                success=False,
                error_message="GEMINI_API_KEY is missing or invalid"
            )

        start_time = time.time()
        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                system_instruction=system_prompt or SYSTEM_PROMPT
            )

            candidate_models = [self.model_name, "gemini-flash-lite-latest", "gemini-3.1-flash-lite", "gemini-2.5-flash-lite"]
            models_to_try = []
            for m in candidate_models:
                if m and m not in models_to_try:
                    models_to_try.append(m)

            response = None
            actual_model = self.model_name
            last_err = None

            for mod in models_to_try:
                try:
                    actual_model = mod
                    response = self._client.models.generate_content(
                        model=mod,
                        contents=prompt,
                        config=config
                    )
                    if response and response.text:
                        break
                except Exception as api_err:
                    last_err = api_err
                    logger.warning(f"[GeminiLLM] โมเดล {mod} ติดขัด ({str(api_err)[:60]}), กำลังลองโมเดลสำรองถัดไป...")
                    continue

            if response is None:
                raise last_err or Exception("All Gemini models exhausted")

            latency = time.time() - start_time
            response_text = response.text.strip() if response.text else ""
            
            # ดึงข้อมูล Token Usage
            prompt_tokens = 0
            candidate_tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                candidate_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

            total_tokens = prompt_tokens + candidate_tokens
            tps = candidate_tokens / latency if latency > 0 else 0.0
            citations = extract_citations(response_text)

            return LLMResponse(
                text=response_text,
                model=actual_model,
                latency_sec=round(latency, 3),
                prompt_tokens=prompt_tokens,
                completion_tokens=candidate_tokens,
                total_tokens=total_tokens,
                tokens_per_sec=round(tps, 2),
                citations=citations,
                success=True
            )

        except Exception as e:
            latency = time.time() - start_time
            return LLMResponse(
                text=f"[เกิดข้อผิดพลาดในการเรียก Gemini API: {str(e)}]",
                model=self.model_name,
                latency_sec=round(latency, 3),
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                tokens_per_sec=0.0,
                citations=[],
                success=False,
                error_message=str(e)
            )

    def answer_rag_query(
        self,
        query: str,
        context: str,
        temperature: float = 0.2
    ) -> LLMResponse:
        """
        ฟังก์ชันสะดวกสำหรับรับ query + context แล้วสร้าง RAG Prompt ส่งให้ Gemini API ทันที
        """
        full_prompt = build_rag_prompt(query=query, context=context)
        return self.generate(prompt=full_prompt, temperature=temperature)
