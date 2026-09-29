"""
src/llm/__init__.py
===================
Package สำหรับจัดการ LLM (Local Ollama 3B/4B, Google Gemini API, และ Comparator)
"""

from src.llm.prompts import (
    SYSTEM_PROMPT,
    PROMPT_TEMPLATE,
    build_rag_prompt,
    extract_citations
)
from src.llm.local_llm import LocalLLMClient, LLMResponse, ALLOWED_3B_4B_MODELS
from src.llm.gemini_llm import GeminiLLMClient
from src.llm.comparator import LLMComparator, ComparisonResult

__all__ = [
    "SYSTEM_PROMPT",
    "PROMPT_TEMPLATE",
    "build_rag_prompt",
    "extract_citations",
    "LocalLLMClient",
    "LLMResponse",
    "ALLOWED_3B_4B_MODELS",
    "GeminiLLMClient",
    "LLMComparator",
    "ComparisonResult"
]
