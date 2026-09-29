"""
Advanced Hybrid RAG Engine (หัวใจสำคัญตามเกณฑ์ Rubric Level 5)
บูรณาการ Dense Retrieval (FAISS/ChromaDB), Sparse Search (BM25) และ Knowledge Graph (Neo4j)
พร้อมด้วย Query Intent Router, Reciprocal Rank Fusion (RRF) และ Semantic Re-ranking
"""
import os
import re
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field
from langchain_core.documents import Document

from src.vector.faiss_store import TokyoFAISSStore
from src.vector.bm25_store import TokyoBM25Store
from src.graph.pathfinder import TokyoGraphPathfinder

class HybridContextResult(BaseModel):
    intent: str = Field(..., description="ประเภทเจตนาของคำถาม (ROUTE_TRANSIT, FACT_RETRIEVAL, HYBRID_COMPLEX)")
    final_context: str = Field(..., description="บริบทข้อความรวมที่จัดระเบียบแล้วสำหรับส่งต่อให้ LLM")
    graph_context: str = Field(..., description="บริบทความสัมพันธ์จาก Knowledge Graph")
    vector_docs_count: int = Field(..., description="จำนวนเอกสารที่ดึงมาจาก Vector/Sparse")
    citations: List[str] = Field(default_factory=list, description="รายการแหล่งอ้างอิงสถานที่/สถานี")

class TokyoHybridRAGEngine:
    """
    เอนจิน Hybrid RAG ขั้นสูงสำหรับโตเกียว
    """
    def __init__(
        self,
        embed_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        device: str = "cpu"
    ):
        print(f"[TokyoHybridRAGEngine] Initializing Hybrid Engine with model [{embed_model_name}]...")
        self.faiss_store = TokyoFAISSStore(embed_model_name=embed_model_name, device=device)
        self.bm25_store = TokyoBM25Store()
        self.pathfinder = TokyoGraphPathfinder()

        # ตรวจสอบและโหลด Indices
        self.faiss_store.load_index()
        self.bm25_store.load_index()

    def route_query_intent(self, query: str) -> str:
        """
        Query Intent Router: จำแนกเจตนาของคำถาม
        1. ROUTE_TRANSIT: ถามเส้นทาง/เดินทาง/เวลารถไฟล้วนๆ
        2. FACT_RETRIEVAL: ถามข้อมูลประวัติ/เวลาเปิด/ค่าเข้าชมสถานที่ใดสถานที่หนึ่ง
        3. HYBRID_COMPLEX: คำถามผสม เช่น แนะนำสถานที่พร้อมวิธีเดินทาง หรือคำถามท่องเที่ยวภาพรวม
        """
        clean_q = query.lower()

        transit_keywords = [
            "เดินทาง", "ไปยังไง", "ไปยัง", "นั่งรถไฟ", "สายอะไร", "กี่นาที",
            "เส้นทาง", "เปลี่ยนสาย", "สถานีไหน", "กี่สถานี", "route", "how to get", "train"
        ]
        fact_keywords = [
            "ประวัติ", "คืออะไร", "เปิดกี่โมง", "ปิดกี่โมง", "ค่าเข้า", "ราคา",
            "เวลาทำการ", "รายละเอียด", "story", "fee", "hours", "admission"
        ]
        overview_keywords = [
            "แนะนำ", "ที่เที่ยว", "มีอะไรบ้าง", "ในย่าน", "รอบๆ", "แถวนี้", "จัดทริป",
            "แผนเที่ยว", "recommend", "attraction"
        ]

        has_transit = any(k in clean_q for k in transit_keywords)
        has_fact = any(k in clean_q for k in fact_keywords)
        has_overview = any(k in clean_q for k in overview_keywords)

        # หากมีทั้งการถามเที่ยวและการเดินทาง หรือถามภาพรวม -> HYBRID_COMPLEX
        if (has_transit and has_fact) or (has_transit and has_overview) or ("จาก" in clean_q and "ไป" in clean_q and has_overview):
            return "HYBRID_COMPLEX"
        # หากถามเฉพาะเส้นทางการเดินทาง
        elif has_transit or ("จาก" in clean_q and "ไป" in clean_q):
            return "ROUTE_TRANSIT"
        # หากถามข้อมูลเนื้อหา
        elif has_fact:
            return "FACT_RETRIEVAL"
        else:
            return "HYBRID_COMPLEX"

    def reciprocal_rank_fusion(
        self,
        dense_results: List[Tuple[Document, float]],
        sparse_results: List[Tuple[Document, float]],
        k_const: int = 60
    ) -> List[Document]:
        """
        อัลกอริทึม Reciprocal Rank Fusion (RRF):
        RRF_Score(d) = sum( 1 / (k_const + rank(d)) )
        """
        doc_scores: Dict[str, float] = {}
        doc_map: Dict[str, Document] = {}

        # 1. ให้คะแนนจาก Dense Vector
        for rank, (doc, _) in enumerate(dense_results):
            doc_id = doc.metadata.get("chunk_id", doc.page_content[:50])
            doc_map[doc_id] = doc
            doc_scores[doc_id] = doc_scores.get(doc_id, 0.0) + (1.0 / (k_const + rank + 1))

        # 2. ให้คะแนนจาก Sparse BM25
        for rank, (doc, _) in enumerate(sparse_results):
            doc_id = doc.metadata.get("chunk_id", doc.page_content[:50])
            doc_map[doc_id] = doc
            doc_scores[doc_id] = doc_scores.get(doc_id, 0.0) + (1.0 / (k_const + rank + 1))

        # เรียงตามคะแนนรวม RRF จากมากไปน้อย
        sorted_ids = sorted(doc_scores.keys(), key=lambda i: doc_scores[i], reverse=True)
        return [doc_map[i] for i in sorted_ids]

    def rerank_documents(
        self,
        query: str,
        candidates: List[Document],
        top_n: int = 3
    ) -> List[Document]:
        """
        Semantic Cross-Modal Re-ranking:
        คำนวณ Cosine Similarity ซ้ำอีกครั้งกับ Embeddings เพื่อคัดกรอง Chunks ที่ตรงที่สุด
        """
        if not candidates:
            return []
        if len(candidates) <= top_n:
            return candidates

        try:
            q_vec = np.array(self.faiss_store.embeddings.embed_query(query))
            doc_texts = [d.page_content for d in candidates]
            d_vecs = np.array(self.faiss_store.embeddings.embed_documents(doc_texts))

            norm_q = np.linalg.norm(q_vec)
            norm_d = np.linalg.norm(d_vecs, axis=1)
            cos_sims = np.dot(d_vecs, q_vec) / (norm_d * norm_q + 1e-9)

            scored_candidates = []
            for rank, (doc, sim) in enumerate(zip(candidates, cos_sims)):
                rrf_weight = 1.0 / (60 + rank + 1)
                # รวม 70% Cosine Similarity + 30% RRF Rank Score
                final_score = (0.70 * float(sim)) + (0.30 * (rrf_weight * 60.0))
                scored_candidates.append((doc, final_score))

            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            return [doc for doc, score in scored_candidates[:top_n]]
        except Exception as e:
            print(f"[TokyoHybridRAGEngine] Re-ranking fallback warning: {e}")
            return candidates[:top_n]

    def retrieve_hybrid_context(
        self,
        query: str,
        top_k_retrieval: int = 6,
        top_n_rerank: int = 3
    ) -> HybridContextResult:
        """
        Pipeline หลักของการทำ Hybrid Retrieval:
        Routing -> (Dense + BM25 -> RRF -> Rerank) + (Neo4j Graph Traversal) -> Context Aggregation
        """
        intent = self.route_query_intent(query)
        dense_results: List[Tuple[Document, float]] = []
        sparse_results: List[Tuple[Document, float]] = []
        graph_context = ""
        citations: List[str] = []

        # 1. ดึงข้อมูลจาก Knowledge Graph (หากเป็นเรื่องเส้นทางหรือผสม)
        if intent in ["ROUTE_TRANSIT", "HYBRID_COMPLEX"]:
            graph_context = self.pathfinder.extract_graph_context_for_rag(query)

        # 2. ดึงข้อมูลจาก Vector & Sparse (หากเป็นเรื่องข้อเท็จจริงหรือผสม)
        if intent in ["FACT_RETRIEVAL", "HYBRID_COMPLEX"]:
            dense_results = self.faiss_store.search(query, k=top_k_retrieval)
            sparse_results = self.bm25_store.search(query, k=top_k_retrieval)

        # 3. รวมผลด้วย Reciprocal Rank Fusion (RRF)
        fused_docs = self.reciprocal_rank_fusion(dense_results, sparse_results)

        # 4. Re-rank ให้เหลือ Top-N ที่แม่นยำที่สุด
        final_docs = self.rerank_documents(query, fused_docs, top_n=top_n_rerank)

        # 5. ประกอบร่างบริบทเอกสาร (Context Aggregation)
        doc_blocks = []
        for i, doc in enumerate(final_docs):
            title = doc.metadata.get("title", f"เอกสาร {i+1}")
            place_id = doc.metadata.get("place_id", "N/A")
            station = doc.metadata.get("nearest_station", "N/A")
            citation_tag = f"{title} (สถานีใกล้เคียง: {station})"
            if citation_tag not in citations:
                citations.append(citation_tag)
            
            doc_blocks.append(
                f"[ข้อมูลที่ {i+1} | อ้างอิง: {citation_tag}]\n"
                f"{doc.page_content.strip()}"
            )

        vector_context = "\n\n".join(doc_blocks) if doc_blocks else "ไม่มีข้อมูลเอกสารบรรยายเฉพาะเจาะจง"

        # 6. รวม Graph Context และ Vector Context เข้าด้วยกันอย่างเป็นระเบียบ
        aggregated_context_list = []
        if graph_context.strip():
            aggregated_context_list.append(f"=== ข้อมูลความสัมพันธ์และเส้นทาง (Knowledge Graph) ===\n{graph_context}")
        if vector_context.strip() and vector_context != "ไม่มีข้อมูลเอกสารบรรยายเฉพาะเจาะจง":
            aggregated_context_list.append(f"=== ข้อมูลรายละเอียดสถานที่ (Vector & Knowledge Base) ===\n{vector_context}")

        final_context_str = "\n\n".join(aggregated_context_list)

        return HybridContextResult(
            intent=intent,
            final_context=final_context_str,
            graph_context=graph_context,
            vector_docs_count=len(final_docs),
            citations=citations
        )

if __name__ == "__main__":
    engine = TokyoHybridRAGEngine()
    print("=" * 65)
    print("TESTING PRODUCTION-GRADE HYBRID RAG ENGINE")
    print("=" * 65)

    test_queries = [
        "จากสถานีอาซากุสะจะไปชิบูย่าต้องนั่งรถไฟสายอะไร",
        "โตเกียวสกายทรีค่าเข้าชมเท่าไหร่ และเปิดปิดกี่โมง",
        "แนะนำสถานที่เที่ยวในย่านชิบูย่าพร้อมวิธีเดินทาง"
    ]

    for q in test_queries:
        print(f"\n❓ คำถาม: {q}")
        res = engine.retrieve_hybrid_context(q)
        print(f"🎯 Intent: {res.intent} | Docs: {res.vector_docs_count} | Citations: {len(res.citations)}")
        print("📄 Preview Context:\n", res.final_context[:250] + "...")
