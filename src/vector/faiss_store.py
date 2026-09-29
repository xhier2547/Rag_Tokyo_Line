"""
FAISS Vector Store Manager
จัดการการสร้าง ดัชนีเวกเตอร์ และการค้นหาด้วย FAISS (Facebook AI Similarity Search)
รองรับการปรับแต่ง Hyperparameters: Top-K, Similarity Threshold และ Distance Metric
"""
import os
import json
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DEFAULT_FAISS_DIR = os.path.join(BASE_DIR, "data", "faiss_index")
CHUNKS_FILE = os.path.join(PROCESSED_DIR, "documents_chunks.json")
DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

class TokyoFAISSStore:
    """
    คลาสจัดการ FAISS Vector Database สำหรับเอกสารท่องเที่ยวโตเกียว
    """
    def __init__(
        self,
        embed_model_name: str = DEFAULT_MODEL,
        index_dir: str = DEFAULT_FAISS_DIR,
        device: str = "cpu"
    ):
        self.embed_model_name = embed_model_name
        self.index_dir = index_dir
        self.device = device
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embed_model_name,
            model_kwargs={'device': self.device}
        )
        self.vectorstore: Optional[FAISS] = None

    def build_from_chunks(self, chunks_path: str = CHUNKS_FILE) -> int:
        """
        อ่านไฟล์ documents_chunks.json และสร้าง FAISS Vector Index
        """
        if not os.path.exists(chunks_path):
            raise FileNotFoundError(f"Chunks file not found at: {chunks_path}")

        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)

        documents: List[Document] = []
        for c in chunks_data:
            # รวมเนื้อหาภาษาไทยและอังกฤษสำหรับ Embedding
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
            documents.append(Document(page_content=combined_text, metadata=metadata))

        print(f"[TokyoFAISSStore] Building FAISS Index with {len(documents)} documents using [{self.embed_model_name}]...")
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        
        os.makedirs(self.index_dir, exist_ok=True)
        self.vectorstore.save_local(self.index_dir)
        print(f"[TokyoFAISSStore] Saved FAISS Index to '{self.index_dir}'")
        return len(documents)

    def load_index(self) -> bool:
        """โหลด FAISS Index จากดิสก์"""
        if os.path.exists(self.index_dir):
            try:
                self.vectorstore = FAISS.load_local(
                    self.index_dir,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return True
            except Exception as e:
                print(f"[TokyoFAISSStore] Warning: Could not load FAISS ({e})")
                return False
        return False

    def search(
        self,
        query: str,
        k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Tuple[Document, float]]:
        """
        ค้นหาเวกเตอร์ที่ใกล้เคียงที่สุด
        คืนค่า: List ของ (Document, Similarity_Score)
        """
        if self.vectorstore is None:
            if not self.load_index():
                self.build_from_chunks()

        # คำนวณ Similarity Search with Score (L2 distance หรือ Cosine distance)
        docs_and_scores = self.vectorstore.similarity_search_with_score(query, k=k)
        
        # ปรับค่า Score ให้อยู่ในรูป Similarity (0.0 - 1.0)
        results = []
        for doc, distance in docs_and_scores:
            # แปลง L2 Distance เป็น Cosine-like Similarity: 1 / (1 + distance)
            similarity = 1.0 / (1.0 + float(distance))
            if score_threshold is None or similarity >= score_threshold:
                results.append((doc, round(similarity, 4)))

        return results
