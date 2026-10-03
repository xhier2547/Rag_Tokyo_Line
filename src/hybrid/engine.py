"""
Advanced Hybrid RAG Engine
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
        self._rerank_embedding_cache: Dict[str, np.ndarray] = {}
        self._prepare_rerank_embeddings()

    def _prepare_rerank_embeddings(self) -> None:
        """Embed the static document corpus once for low-latency re-ranking."""
        documents = self.bm25_store.documents
        if not documents:
            return
        try:
            vectors = self.faiss_store.embeddings.embed_documents(
                [doc.page_content for doc in documents]
            )
            for doc, vector in zip(documents, vectors):
                doc_id = doc.metadata.get("chunk_id", doc.page_content[:50])
                self._rerank_embedding_cache[doc_id] = np.asarray(vector, dtype=float)
        except Exception:
            # Search still works through RRF if precomputation is unavailable.
            self._rerank_embedding_cache = {}

    def route_query_intent(self, query: str) -> str:
        """
        Query Intent Router: จำแนกเจตนาของคำถาม
        1. ROUTE_TRANSIT: ถามเส้นทาง/เดินทาง/เวลารถไฟล้วนๆ
        2. FACT_RETRIEVAL: ถามข้อมูลประวัติ/เวลาเปิด/ค่าเข้าชมสถานที่ใดสถานที่หนึ่งเดี่ยวๆ โดยไม่มีมิติเชิงพื้นที่
        3. HYBRID_COMPLEX: คำถามผสม เช่น ค้นหาเชิงพื้นที่ (Spatial / Multi-hop), แนะนำสถานที่พร้อมการเดินทาง หรือจัดทริป
        """
        clean_q = query.lower()

        transit_keywords = [
            "เดินทาง", "ไปยังไง", "ไปยัง", "นั่งรถไฟ", "สายอะไร", "กี่นาที",
            "เส้นทาง", "เปลี่ยนสาย", "สถานีไหน", "กี่สถานี", "route", "how to get", "train"
        ]
        spatial_keywords = [
            "ใกล้", "ระยะเดิน", "เดินถึง", "สถานี", "เขตเดียวกัน", "ห่างจาก", "ห่างกัน",
            "เชื่อมต่อ", "ติดกับ", "ย่าน", "รอบๆ", "ละแวก", "กิโลเมตร", "km", "ในเขต",
            "ต่อเนื่อง", "แวะ", "ไม่ย้อน"
        ]
        fact_keywords = [
            "ประวัติ", "คืออะไร", "เปิดกี่โมง", "ปิดกี่โมง", "ค่าเข้า", "ราคา",
            "เวลาทำการ", "รายละเอียด", "story", "fee", "hours", "admission"
        ]
        overview_keywords = [
            "แนะนำ", "ที่เที่ยว", "มีอะไรบ้าง", "ในย่าน", "รอบๆ", "แถวนี้", "จัดทริป",
            "แผนเที่ยว", "recommend", "attraction", "จัดเส้นทาง", "ทริป"
        ]

        has_transit = any(k in clean_q for k in transit_keywords)
        has_spatial = any(k in clean_q for k in spatial_keywords)
        has_fact = any(k in clean_q for k in fact_keywords)
        has_overview = any(k in clean_q for k in overview_keywords)

        # เส้นทางจากต้นทางไปปลายทางที่มีคำบ่งชี้รถไฟชัดเจนเป็น transit
        # แม้คำถามจะมีคำว่า "สถานี" ซึ่งใช้ร่วมกับ spatial queries ด้วย
        if has_transit and "จาก" in clean_q and "ไป" in clean_q and not has_overview and not has_fact:
            return "ROUTE_TRANSIT"
        # คำถามเชิงพื้นที่ (Spatial / Multi-hop / Proximity) หรือคำถามภาพรวมผสม
        if has_spatial or (has_transit and has_fact) or (has_transit and has_overview) or ("จาก" in clean_q and "ไป" in clean_q and (has_overview or has_spatial)):
            return "HYBRID_COMPLEX"
        # หากถามเฉพาะเส้นทางการเดินทางล้วนๆ
        elif has_transit or ("จาก" in clean_q and "ไป" in clean_q):
            return "ROUTE_TRANSIT"
        # หากถามข้อมูลข้อเท็จจริงเดี่ยวๆ
        elif has_fact:
            return "FACT_RETRIEVAL"
        else:
            return "HYBRID_COMPLEX"

    @staticmethod
    def expand_query(query: str) -> str:
        """Add compact domain terms for common Thai/English paraphrases.

        The original user text is always kept first.  Expansion is deliberately
        small so it improves recall without turning every question into the same
        generic Tokyo query.
        """
        clean_q = query.lower()
        groups = [
            (["ฟรี", "ไม่เสียค่า", "ไม่เสียเงิน", "free"], "ค่าเข้าชมฟรี free admission"),
            (["คนเดียว", "เที่ยวเดี่ยว", "solo"], "เที่ยวคนเดียว solo travel เดินเล่น"),
            (["ไม่ยอดนิยม", "คนไม่เยอะ", "เงียบ", "hidden gem"], "สถานที่เงียบสงบ hidden gem ไม่แออัด"),
            (["ครึ่งวัน", "3 ชั่วโมง", "สามชั่วโมง"], "แผนเที่ยวระยะสั้น half day itinerary"),
            (["เด็ก", "ครอบครัว", "family"], "เหมาะสำหรับครอบครัวและเด็ก family friendly"),
            (["อนิเมะ", "anime", "เกม", "gaming", "โปเกมอน", "pokemon"], "อนิเมะ เกม เทคโนโลยี pop culture"),
            (["อาหาร", "ของกิน", "กิน", "ตลาด", "street food"], "อาหาร ตลาด ของกิน สตรีทฟู้ด food market"),
            (["สวน", "ธรรมชาติ", "ซากุระ", "พักผ่อน"], "สวน ธรรมชาติ จุดชมวิว nature park"),
            (["ช้อป", "shopping", "แฟชั่น", "เสื้อผ้า"], "ช้อปปิ้ง แฟชั่น shopping district"),
            (["ใกล้", "เดินถึง", "ระยะเดิน", "แถว", "รอบ"], "สถานีใกล้เคียง ระยะเดิน nearby station walking"),
        ]
        additions = [expansion for aliases, expansion in groups if any(alias in clean_q for alias in aliases)]
        return query if not additions else f"{query} {' '.join(dict.fromkeys(additions))}"

    def reciprocal_rank_fusion(
        self,
        dense_results: List[Tuple[Document, float]],
        sparse_results: List[Tuple[Document, float]],
        k_const: int = 60,
        dense_weight: float = 1.0,
        sparse_weight: float = 1.0,
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
            doc_scores[doc_id] = doc_scores.get(doc_id, 0.0) + (dense_weight / (k_const + rank + 1))

        # 2. ให้คะแนนจาก Sparse BM25
        for rank, (doc, _) in enumerate(sparse_results):
            doc_id = doc.metadata.get("chunk_id", doc.page_content[:50])
            doc_map[doc_id] = doc
            doc_scores[doc_id] = doc_scores.get(doc_id, 0.0) + (sparse_weight / (k_const + rank + 1))

        # เรียงตามคะแนนรวม RRF จากมากไปน้อย
        sorted_ids = sorted(doc_scores.keys(), key=lambda i: doc_scores[i], reverse=True)
        max_score = max(doc_scores.values(), default=1.0)
        ranked_docs = []
        for doc_id in sorted_ids:
            doc = doc_map[doc_id]
            doc.metadata["rrf_score"] = doc_scores[doc_id]
            doc.metadata["rrf_score_normalized"] = doc_scores[doc_id] / max_score
            ranked_docs.append(doc)
        return ranked_docs

    def rerank_documents(
        self,
        query: str,
        candidates: List[Document],
        top_n: int = 3,
        intent: str = "FACT_RETRIEVAL",
        graph_ranked_entities: Optional[List[str]] = None,
    ) -> List[Document]:
        """
        Semantic re-ranking using the same embedding model as the FAISS index.
        The score blends semantic similarity, RRF rank and a graph entity boost.
        - หากเป็นคำถามภาพรวม/แนะนำ: ใช้ Diversity-Aware คัดเลือกสถานที่ (place_id) ไม่ให้ซ้ำ
        - หากเป็นคำถามเจาะจง: คัดเลือก Top-N Chunks ที่มีคะแนน RRF สูงสุดตามลำดับ
        """
        if not candidates:
            return []
        graph_ranked_entities = graph_ranked_entities or []
        graph_rank = {entity_id: rank for rank, entity_id in enumerate(graph_ranked_entities, start=1)}

        try:
            query_vec = np.asarray(self.faiss_store.embeddings.embed_query(query), dtype=float)
            doc_vec_list = []
            missing_docs = []
            missing_indices = []
            for index, doc in enumerate(candidates):
                doc_id = doc.metadata.get("chunk_id", doc.page_content[:50])
                vector = self._rerank_embedding_cache.get(doc_id)
                if vector is None:
                    missing_docs.append(doc.page_content)
                    missing_indices.append(index)
                    doc_vec_list.append(None)
                else:
                    doc_vec_list.append(vector)
            if missing_docs:
                new_vectors = self.faiss_store.embeddings.embed_documents(missing_docs)
                for index, vector in zip(missing_indices, new_vectors):
                    array = np.asarray(vector, dtype=float)
                    doc_vec_list[index] = array
                    doc = candidates[index]
                    doc_id = doc.metadata.get("chunk_id", doc.page_content[:50])
                    self._rerank_embedding_cache[doc_id] = array
            doc_vecs = np.asarray(doc_vec_list, dtype=float)
            query_norm = np.linalg.norm(query_vec) or 1.0
            doc_norms = np.linalg.norm(doc_vecs, axis=1)
            semantic_scores = (doc_vecs @ query_vec) / np.maximum(doc_norms * query_norm, 1e-12)
        except Exception:
            # Retrieval remains available even if a backend cannot batch-embed.
            semantic_scores = np.zeros(len(candidates), dtype=float)

        scored = []
        for index, doc in enumerate(candidates):
            semantic = float((semantic_scores[index] + 1.0) / 2.0)
            rrf = float(doc.metadata.get("rrf_score_normalized", 0.0))
            entity_id = doc.metadata.get("place_id", "")
            graph = 1.0 / graph_rank[entity_id] if entity_id in graph_rank else 0.0
            if intent == "ROUTE_TRANSIT":
                weights = (0.40, 0.20, 0.40)
            elif intent == "FACT_RETRIEVAL":
                weights = (0.65, 0.30, 0.05)
            else:
                weights = (0.50, 0.25, 0.25)
            final_score = weights[0] * semantic + weights[1] * rrf + weights[2] * graph
            doc.metadata["rerank_score"] = round(final_score, 6)
            scored.append((final_score, doc))
        candidates = [doc for _, doc in sorted(scored, key=lambda item: item[0], reverse=True)]

        # ตรวจสอบว่าคำถามต้องการกระจายสถานที่หรือไม่ (เช่น แนะนำ 5 ที่, ทริป)
        is_recommendation = any(kw in query.lower() for kw in ["แนะนำ", "ที่เที่ยว", "จัดทริป", "มีที่ไหนบ้าง", "ไฮไลท์", "5", "10"])

        selected_docs: List[Document] = []
        if is_recommendation and intent != "FACT_RETRIEVAL":
            # Diversity-Aware Selection: เลือกสถานที่ (place_id) ไม่ให้ซ้ำ เพื่อแนะนำได้หลายแห่ง
            seen_places = set()
            for doc in candidates:
                place_id = doc.metadata.get("place_id") or doc.metadata.get("title", "")
                if place_id not in seen_places:
                    seen_places.add(place_id)
                    selected_docs.append(doc)
                    if len(selected_docs) >= top_n:
                        break

            # หากจำนวนยังไม่ครบ ให้เติม Chunks ที่เหลือ
            if len(selected_docs) < top_n:
                for doc in candidates:
                    if doc not in selected_docs:
                        selected_docs.append(doc)
                        if len(selected_docs) >= top_n:
                            break
        else:
            # คำถามเจาะจง/ค้นหาข้อเท็จจริง: เลือก Chunks ที่คะแนน RRF สูงสุดตามลำดับ
            selected_docs = candidates[:top_n]

        return selected_docs

    def retrieve_hybrid_context(
        self,
        query: str,
        top_k_retrieval: int = 15,
        top_n_rerank: int = 5
    ) -> HybridContextResult:
        """
        Pipeline หลักของการทำ Hybrid Retrieval:
        Routing -> (Dense + BM25 -> RRF -> Rerank) + (Neo4j Graph Traversal) -> Context Aggregation
        """
        intent = self.route_query_intent(query)
        clean_q = query.lower()
        retrieval_query = self.expand_query(query)

        # ปรับ Top-N อัตโนมัติหากเป็นคำถามที่ต้องการคำแนะนำหลายสถานที่ (เช่น แนะนำ 5 สถานที่, ยอดนิยม)
        recommend_keywords = ["5", "10", "แนะนำ", "ยอดนิยม", "ที่เที่ยว", "จัดทริป", "มีที่ไหนบ้าง", "ไฮไลท์", "แลนด์มาร์ก"]
        if any(kw in clean_q for kw in recommend_keywords):
            top_n_rerank = max(top_n_rerank, 8)
            top_k_retrieval = max(top_k_retrieval, 15)

        dense_results: List[Tuple[Document, float]] = []
        sparse_results: List[Tuple[Document, float]] = []
        graph_context = ""
        citations: List[str] = []

        # 1. ดึงข้อมูลจาก Knowledge Graph เพื่อหาความสัมพันธ์เชิงพื้นที่/เส้นทาง/ข้อมูลจำเพาะของโหนด
        graph_context = self.pathfinder.extract_graph_context_for_rag(query)
        graph_ranked_entities = self.pathfinder.retrieve_ranked_entities(query)

        # 2. ดึงข้อมูลจาก Vector & Sparse Retrieval
        dense_results = self.faiss_store.search(retrieval_query, k=top_k_retrieval)
        sparse_results = self.bm25_store.search(retrieval_query, k=top_k_retrieval)

        # 3. รวมผลด้วย Reciprocal Rank Fusion (RRF)
        if intent == "FACT_RETRIEVAL":
            dense_weight, sparse_weight = 1.15, 1.0
        elif intent == "ROUTE_TRANSIT":
            dense_weight, sparse_weight = 0.85, 1.15
        else:
            dense_weight, sparse_weight = 1.0, 1.0
        fused_docs = self.reciprocal_rank_fusion(
            dense_results,
            sparse_results,
            dense_weight=dense_weight,
            sparse_weight=sparse_weight,
        )

        # 4. Re-rank ให้เหลือ Top-N ที่แม่นยำที่สุด
        final_docs = self.rerank_documents(
            retrieval_query,
            fused_docs,
            top_n=top_n_rerank,
            intent=intent,
            graph_ranked_entities=graph_ranked_entities,
        )

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
