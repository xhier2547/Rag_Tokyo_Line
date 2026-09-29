"""
BM25 Sparse Keyword Index Manager
จัดการการสกัดคำและคำนวณคะแนนความเกี่ยวข้องด้วย BM25 (Okapi BM25)
ใช้ PyThaiNLP เพื่อตัดคำภาษาไทยอย่างถูกต้อง ผสานกับคำภาษาอังกฤษและชื่อเฉพาะ
"""
import os
import json
import pickle
import re
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi
from pythainlp.tokenize import word_tokenize
from langchain_core.documents import Document

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DEFAULT_BM25_DIR = os.path.join(BASE_DIR, "data", "bm25_index")
BM25_FILE = os.path.join(DEFAULT_BM25_DIR, "bm25_data.pkl")
CHUNKS_FILE = os.path.join(PROCESSED_DIR, "documents_chunks.json")

def tokenize_corpus_text(text: str) -> List[str]:
    """
    ตัดคำข้อความผสม (ไทย + อังกฤษ + รหัส) ให้พร้อมสำหรับ BM25
    """
    if not text:
        return []
    # แปลงอักษรเป็นตัวพิมพ์เล็ก
    clean_t = text.lower()
    # ตัดคำภาษาไทยด้วย newmm
    tokens = word_tokenize(clean_t, engine="newmm")
    cleaned_tokens = []
    for t in tokens:
        t_strip = t.strip()
        # ขจัดสัญลักษณ์และช่องว่าง
        if t_strip and len(t_strip) > 1 and not re.match(r'^[\s\.,;:\?!\"\'\(\)\[\]\{\}]+$', t_strip):
            cleaned_tokens.append(t_strip)
    return cleaned_tokens

class TokyoBM25Store:
    """
    คลาสจัดการ BM25 Sparse Search Engine สำหรับโตเกียว
    """
    def __init__(self, index_file: str = BM25_FILE):
        self.index_file = index_file
        self.bm25: BM25Okapi = None
        self.documents: List[Document] = []

    def build_from_chunks(self, chunks_path: str = CHUNKS_FILE) -> int:
        """สร้าง BM25 Index จากไฟล์ documents_chunks.json"""
        if not os.path.exists(chunks_path):
            raise FileNotFoundError(f"Chunks file not found at: {chunks_path}")

        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)

        self.documents = []
        tokenized_corpus = []

        for c in chunks_data:
            combined_text = f"{c['title']}\n{c['content_th']}\n{c.get('content_en', '')}".strip()
            metadata = {
                "chunk_id": c["chunk_id"],
                "place_id": c["place_id"],
                "title": c["title"],
                "ward": c.get("ward", ""),
                "category": c.get("category", ""),
                "nearest_station": c.get("nearest_station", ""),
                "walk_time_min": c.get("walk_time_min", 0),
                "tags": ";".join(c.get("tags", []))
            }
            doc = Document(page_content=combined_text, metadata=metadata)
            self.documents.append(doc)
            tokens = tokenize_corpus_text(combined_text)
            tokenized_corpus.append(tokens)

        print(f"[TokyoBM25Store] Building BM25 index with {len(self.documents)} documents...")
        self.bm25 = BM25Okapi(tokenized_corpus)

        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        with open(self.index_file, "wb") as f:
            pickle.dump({
                "bm25": self.bm25,
                "documents": self.documents
            }, f)
        print(f"[TokyoBM25Store] Saved BM25 index to '{self.index_file}'")
        return len(self.documents)

    def load_index(self) -> bool:
        """โหลด BM25 Index จากไฟล์ pickle"""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "rb") as f:
                    data = pickle.load(f)
                    self.bm25 = data["bm25"]
                    self.documents = data["documents"]
                return True
            except Exception as e:
                print(f"[TokyoBM25Store] Warning: Could not load BM25 ({e})")
                return False
        return False

    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """
        ค้นหาข้อความด้วย BM25 Keyword Scoring
        คืนค่า: List ของ (Document, BM25_Score) เรียงจากมากไปน้อย
        """
        if self.bm25 is None or not self.documents:
            if not self.load_index():
                self.build_from_chunks()

        query_tokens = tokenize_corpus_text(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score > 0.0:
                results.append((self.documents[idx], round(score, 4)))
        return results
