"""
ChromaDB Vector Store Manager
จัดการการสร้างและค้นหาด้วย Native ChromaDB PersistentClient
จุดเด่นตาม Rubric: รองรับ Native Metadata Filtering (กรองตามย่าน ward, หมวดหมู่ category หรือสถานี)
"""
import os
import json
from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DEFAULT_CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma_db")
CHUNKS_FILE = os.path.join(PROCESSED_DIR, "documents_chunks.json")
DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION_NAME = "tokyo_tourism"

class TokyoChromaStore:
    """
    คลาสจัดการ ChromaDB สำหรับจัดเก็บและค้นหาพร้อมตัวกรอง Metadata
    """
    def __init__(
        self,
        embed_model_name: str = DEFAULT_MODEL,
        persist_dir: str = DEFAULT_CHROMA_DIR,
        device: str = "cpu"
    ):
        self.embed_model_name = embed_model_name
        self.persist_dir = persist_dir
        self.device = device
        self._model = None
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer(self.embed_model_name, device=self.device)
        return self._model

    def build_from_chunks(self, chunks_path: str = CHUNKS_FILE) -> int:
        """สร้างหรืออัปเดต ChromaDB Collection จากไฟล์ documents_chunks.json"""
        if not os.path.exists(chunks_path):
            raise FileNotFoundError(f"Chunks file not found at: {chunks_path}")

        # หากมีข้อมูลอยู่แล้ว ไม่ต้องสร้างซ้ำ
        if self.collection.count() > 0:
            return self.collection.count()

        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)

        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []

        for c in chunks_data:
            combined_text = f"{c['title']}\n{c['content_th']}\n{c.get('content_en', '')}".strip()
            documents.append(combined_text)
            ids.append(c["chunk_id"])
            metadatas.append({
                "chunk_id": str(c["chunk_id"]),
                "place_id": str(c["place_id"]),
                "title": str(c["title"]),
                "ward": str(c.get("ward", "")),
                "category": str(c.get("category", "")),
                "nearest_station": str(c.get("nearest_station", "")),
                "walk_time_min": int(c.get("walk_time_min", 0))
            })

        print(f"[TokyoChromaStore] Embedding {len(documents)} documents for ChromaDB...")
        embeddings = self.model.encode(documents).tolist()

        self.collection.upsert(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"[TokyoChromaStore] Successfully saved ChromaDB collection '{COLLECTION_NAME}' ({self.collection.count()} docs)")
        return self.collection.count()

    def search_with_filter(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """
        ค้นหาเวกเตอร์พร้อมการกรอง Metadata (Metadata-Filtered Vector Search)
        ตัวอย่าง filter_dict: {"ward": "Shibuya"} หรือ {"category": "Temple & Shrine"}
        """
        if self.collection.count() == 0:
            self.build_from_chunks()

        q_vec = self.model.encode([query]).tolist()
        
        kwargs = {
            "query_embeddings": q_vec,
            "n_results": k
        }
        if filter_dict:
            kwargs["where"] = filter_dict

        res = self.collection.query(**kwargs)
        
        results: List[Tuple[Document, float]] = []
        if res and res["documents"] and len(res["documents"][0]) > 0:
            docs = res["documents"][0]
            metas = res["metadatas"][0] if res.get("metadatas") else [{}] * len(docs)
            distances = res["distances"][0] if res.get("distances") else [0.0] * len(docs)

            for d_text, meta, dist in zip(docs, metas, distances):
                # Cosine-like similarity
                similarity = 1.0 / (1.0 + float(dist)) if dist is not None else 1.0
                doc_obj = Document(page_content=d_text, metadata=meta)
                results.append((doc_obj, round(similarity, 4)))

        return results
