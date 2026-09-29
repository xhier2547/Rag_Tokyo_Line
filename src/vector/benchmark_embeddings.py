"""
Embedding Model Benchmark Module (Rubric Level 5 Requirement)
เปรียบเทียบโมเดล Embedding ยอดนิยมสำหรับภาษาไทย/อังกฤษ/ญี่ปุ่น
วัด Indexing Time, Query Latency และ Hit Rate เพื่อใช้ประกอบในเล่มรายงาน
"""
import os
import time
import json
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
CHUNKS_FILE = os.path.join(PROCESSED_DIR, "documents_chunks.json")
BENCHMARK_OUTPUT = os.path.join(PROCESSED_DIR, "embedding_benchmark_results.json")

# รายชื่อโมเดลที่ต้องการเปรียบเทียบ
CANDIDATE_MODELS = [
    {
        "name": "paraphrase-multilingual-MiniLM-L12-v2",
        "model_id": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "description": "โมเดลขนาดเล็ก น้ำหนักเบา ประมวลผลเร็วบน CPU"
    },
    {
        "name": "multilingual-e5-small",
        "model_id": "intfloat/multilingual-e5-small",
        "description": "โมเดลตระกูล E5 ขนาดกะทัดรัด ความแม่นยำสูง"
    }
]

# ชุดคำถามทดสอบวัดความแม่นยำ (Ground Truth Benchmark)
BENCHMARK_QUERIES = [
    {
        "query": "วัดเก่าแก่ในอาซากุสะ โคมแดงยักษ์",
        "expected_place": "P_SENSOJI"
    },
    {
        "query": "จุดชมวิวหอคอยกระจายเสียงสูงที่สุดในโลก",
        "expected_place": "P_TOKYO_SKYTREE"
    },
    {
        "query": "ห้าแยกคนข้ามมากที่สุด และรูปปั้นสุนัขฮาจิโกะ",
        "expected_place": "P_SHIBUYA_CROSSING"
    },
    {
        "query": "ตลาดปลา ซาชิมิสด สตรีทฟู้ด",
        "expected_place": "P_TSUKIJI_OUTER"
    },
    {
        "query": "ย่านโอตาคุ แหล่งอนิเมะ ฟิกเกอร์ และเกมอาร์เคด",
        "expected_place": "P_AKIHABARA_ELECTRIC"
    }
]

def run_embedding_benchmark(output_path: str = BENCHMARK_OUTPUT) -> Dict[str, Any]:
    """
    รันการทดสอบเปรียบเทียบโมเดล Embedding และบันทึกผลลง JSON
    """
    if not os.path.exists(CHUNKS_FILE):
        raise FileNotFoundError(f"Chunks file not found: {CHUNKS_FILE}")

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks_data = json.load(f)

    documents = []
    for c in chunks_data:
        text = f"{c['title']}\n{c['content_th']}\n{c.get('content_en', '')}".strip()
        documents.append(Document(page_content=text, metadata=c))

    results = {}
    print(f"\n=== Starting Embedding Models Benchmark ({len(CANDIDATE_MODELS)} models) ===")

    for m in CANDIDATE_MODELS:
        m_id = m["model_id"]
        m_name = m["name"]
        print(f"\n--- Testing Model: {m_name} ---")

        try:
            # 1. วัดเวลาการโหลดโมเดลและสร้าง Index
            t0 = time.time()
            embeddings = HuggingFaceEmbeddings(model_name=m_id, model_kwargs={'device': 'cpu'})
            vectorstore = FAISS.from_documents(documents, embeddings)
            build_time_sec = round(time.time() - t0, 3)
            print(f" Build & Index Time: {build_time_sec} s")

            # 2. วัด Query Latency และ Hit Rate
            latencies = []
            hit_at_1 = 0
            hit_at_3 = 0

            for test_case in BENCHMARK_QUERIES:
                q = test_case["query"]
                exp_place = test_case["expected_place"]

                t_query_start = time.time()
                retrieved_docs = vectorstore.similarity_search(q, k=3)
                latency_ms = (time.time() - t_query_start) * 1000.0
                latencies.append(latency_ms)

                retrieved_places = [d.metadata.get("place_id") for d in retrieved_docs]
                if retrieved_places and retrieved_places[0] == exp_place:
                    hit_at_1 += 1
                if exp_place in retrieved_places:
                    hit_at_3 += 1

            total_q = len(BENCHMARK_QUERIES)
            avg_latency_ms = round(sum(latencies) / total_q, 2)
            hit1_rate = round(hit_at_1 / total_q, 2)
            hit3_rate = round(hit_at_3 / total_q, 2)

            print(f" Avg Query Latency: {avg_latency_ms} ms")
            print(f" Hit@1: {hit1_rate * 100}% | Hit@3: {hit3_rate * 100}%")

            results[m_name] = {
                "model_id": m_id,
                "description": m["description"],
                "build_time_sec": build_time_sec,
                "avg_query_latency_ms": avg_latency_ms,
                "hit_at_1_rate": hit1_rate,
                "hit_at_3_rate": hit3_rate,
                "total_queries_tested": total_q
            }
        except Exception as e:
            print(f" Error benchmarking {m_name}: {e}")
            results[m_name] = {"error": str(e)}

    # บันทึกผลลัพธ์
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n Saved Embedding Benchmark Results to '{output_path}'")
    return results

if __name__ == "__main__":
    run_embedding_benchmark()
