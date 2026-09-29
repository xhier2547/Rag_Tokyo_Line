"""
src/llm/local_llm.py
====================
โมดูลเชื่อมต่อ Local LLM ผ่าน Ollama สำหรับ Tokyo Hybrid Graph RAG
- บังคับใช้เฉพาะโมเดลขนาด 3B - 4B ตามข้อกำหนด (เช่น qwen2.5:3b, gemma3:4b, typhoon2.1-gemma3-4b)
- รองรับการวัดผล Response Time (Latency), Token Usage และ Throughput (Tokens/sec)
- มีระบบ Health Check และ Fallback Error Handling กรณี Ollama ยังไม่ได้เปิด
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import requests
from dotenv import load_dotenv

from src.llm.prompts import SYSTEM_PROMPT, build_rag_prompt, extract_citations

load_dotenv()
logger = logging.getLogger(__name__)

# รายการโมเดลที่แนะนำในกลุ่ม 3B - 4B (ไม่อนุญาตให้ใช้โมเดลเกิน 4B ตามข้อกำหนด)
ALLOWED_3B_4B_MODELS = [
    "qwen2.5:3b",
    "gemma3:4b",
    "hf.co/typhoon-ai/typhoon2.1-gemma3-4b-gguf:Q4_K_M",
    "qwen3.5:4b",
    "llama3.2:3b",
    "qwen3.5:2b",
    "llama3.2:1b"
]


@dataclass
class LLMResponse:
    """โครงสร้างข้อมูลผลลัพธ์จาก LLM พร้อมเมตริกที่วัดได้"""
    text: str
    model: str
    latency_sec: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    tokens_per_sec: float = 0.0
    citations: List[str] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None

    @property
    def error(self) -> Optional[str]:
        return self.error_message




class LocalLLMClient:
    """
    Client สำหรับเชื่อมต่อ Ollama API บนเครื่อง Local (เฉพาะโมเดลขนาด 3B-4B)
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: int = 60
    ):
        """
        เริ่มต้น LocalLLMClient
        
        Args:
            base_url: URL ของ Ollama (ค่าเริ่มต้นอ่านจาก OLLAMA_BASE_URL ใน .env)
            model_name: ชื่อโมเดล (ค่าเริ่มต้นอ่านจาก LOCAL_LLM_MODEL ใน .env โดยต้องเป็น 3B-4B)
            timeout: เวลารอสูงสุดของการเรียก API (วินาที)
        """
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        default_model = os.getenv("LOCAL_LLM_MODEL", "qwen2.5:3b")
        self.model_name = model_name or default_model
        self.timeout = timeout
        
        # ตรวจสอบขนาดโมเดลไม่ให้เกิน 4B ตามที่ผู้ใช้กำหนด
        self._validate_model_size(self.model_name)

    def _validate_model_size(self, model: str) -> None:
        """ตรวจสอบและเตือนหากโมเดลมีขนาดเกิน 4B"""
        lower = model.lower()
        if "7b" in lower or "8b" in lower or "13b" in lower or "70b" in lower:
            logger.warning(
                f"[LocalLLM] คำเตือน: โมเดล '{model}' อาจมีขนาดเกิน 4B ตามข้อกำหนด 3B-4B! "
                f"แนะนำให้ใช้โมเดลในกลุ่ม 3B-4B เช่น {ALLOWED_3B_4B_MODELS[:3]}"
            )

    def check_health(self) -> Dict[str, Any]:
        """
        ตรวจสอบสถานะการทำงานของ Ollama daemon และแสดงโมเดล 3B-4B ที่พร้อมใช้งาน
        """
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                models_data = resp.json().get("models", [])
                available_names = [m.get("name") for m in models_data]
                available_3b_4b = [
                    name for name in available_names 
                    if any(cand.lower() in name.lower() for cand in ["3b", "4b", "2b", "1b"])
                ]
                return {
                    "status": "online",
                    "base_url": self.base_url,
                    "active_model": self.model_name,
                    "available_3b_4b_models": available_3b_4b,
                    "all_installed_models": available_names
                }
            return {"status": "error", "code": resp.status_code}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024
    ) -> LLMResponse:
        """
        ส่งคำสั่งให้ Local LLM (Ollama) ประมวลผลและสร้างคำตอบ
        
        Args:
            prompt: ข้อความคำถามหรือ Full Prompt
            system_prompt: System prompt (หากมี)
            temperature: ค่าความสร้างสรรค์ (0.0-1.0 แนะนำ 0.1-0.3 สำหรับความแม่นยำสูง)
            max_tokens: จำนวน token สูงสุดที่ตอบ
            
        Returns:
            LLMResponse: ผลลัพธ์พร้อมเวลาและสถิติ token
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        start_time = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            latency = time.time() - start_time
            
            if resp.status_code != 200:
                return LLMResponse(
                    text="",
                    model=self.model_name,
                    latency_sec=round(latency, 3),
                    prompt_tokens=0,
                    completion_tokens=0,
                    total_tokens=0,
                    tokens_per_sec=0.0,
                    citations=[],
                    success=False,
                    error_message=f"Ollama API Error HTTP {resp.status_code}: {resp.text}"
                )

            data = resp.json()
            response_text = data.get("response", "").strip()
            prompt_eval_count = data.get("prompt_eval_count", 0)
            eval_count = data.get("eval_count", 0)
            eval_duration_ns = data.get("eval_duration", 0)
            
            # คำนวณ throughput (tokens per second)
            tps = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else (eval_count / latency if latency > 0 else 0.0)
            
            citations = extract_citations(response_text)

            return LLMResponse(
                text=response_text,
                model=self.model_name,
                latency_sec=round(latency, 3),
                prompt_tokens=prompt_eval_count,
                completion_tokens=eval_count,
                total_tokens=prompt_eval_count + eval_count,
                tokens_per_sec=round(tps, 2),
                citations=citations,
                success=True
            )

        except requests.exceptions.ConnectionError:
            latency = time.time() - start_time
            return LLMResponse(
                text="[ระบบแจ้งเตือน] ไม่สามารถเชื่อมต่อ Local Ollama ได้ กรุณาเปิดโปรแกรม Ollama หรือตรวจสอบ URL",
                model=self.model_name,
                latency_sec=round(latency, 3),
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                tokens_per_sec=0.0,
                citations=[],
                success=False,
                error_message="ConnectionError: Ollama daemon is not responding."
            )
        except Exception as e:
            latency = time.time() - start_time
            return LLMResponse(
                text=f"[เกิดข้อผิดพลาดในการประมวลผล Local LLM: {str(e)}]",
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
        ฟังก์ชันสะดวกสำหรับรับ query + context แล้วสร้าง RAG Prompt ส่งให้ Local LLM ทันที
        """
        full_prompt = build_rag_prompt(query=query, context=context)
        return self.generate(prompt=full_prompt, temperature=temperature)
