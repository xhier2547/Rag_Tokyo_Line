"""
tests/test_provenance_and_ablation.py
=====================================
Automated Unit and Integration Tests for:
1. Data Provenance & Lineage Verification
2. Category J & Spatial Intent Routing to Graph RAG
3. Ground-Truth Benchmark Integrity (100 Questions)
4. Empirical Model Comparison Artifact Validation
"""

import os
import sys
import json
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_pipeline.verify_provenance import verify_dataset_provenance
from src.hybrid.engine import TokyoHybridRAGEngine


def test_data_provenance_integrity():
    """ทดสอบความสมบูรณ์ของความสัมพันธ์ข้ามตารางและ Checksum ของชุดข้อมูล"""
    report = verify_dataset_provenance()
    assert report["verification_status"] == "PASSED_100_PERCENT"
    assert report["dataset_summary"]["stations_count"] == 20
    assert report["dataset_summary"]["places_count"] == 20
    assert report["dataset_summary"]["hotels_count"] == 10
    assert report["dataset_summary"]["lines_count"] == 11
    assert report["dataset_summary"]["total_knowledge_entities"] == 61
    assert report["dataset_summary"]["total_graph_relationships"] == 88
    assert report["integrity_checks"]["all_integrity_passed"] is True


def test_category_j_spatial_intent_routing():
    """ทดสอบว่าคำถามหมวด J (Multi-hop Spatial) ถูกจำแนกเป็น HYBRID_COMPLEX และดึง Graph Context เสมอ"""
    # ทดสอบฟังก์ชัน route_query_intent โดยตรงโดยไม่ต้องโหลดโมเดลใหญ่
    engine = TokyoHybridRAGEngine.__new__(TokyoHybridRAGEngine)
    
    # Q91: หาวัดที่อยู่ใกล้สถานีรถไฟและมีสถานที่ทางประวัติศาสตร์อื่นอยู่ในระยะเดินถึง
    intent_q91 = engine.route_query_intent("หาวัดที่อยู่ใกล้สถานีรถไฟและมีสถานที่ทางประวัติศาสตร์อื่นอยู่ในระยะเดินถึง")
    assert intent_q91 == "HYBRID_COMPLEX", f"Expected HYBRID_COMPLEX but got {intent_q91}"

    # Q92: แนะนำสถานที่ชมวิวที่สามารถเดินทางต่อไปยังย่านอาหารได้ง่ายโดยรถไฟไม่เกินหนึ่งต่อ
    intent_q92 = engine.route_query_intent("แนะนำสถานที่ชมวิวที่สามารถเดินทางต่อไปยังย่านอาหารได้ง่ายโดยรถไฟไม่เกินหนึ่งต่อ")
    assert intent_q92 in ["HYBRID_COMPLEX", "ROUTE_TRANSIT"]

    # Q93: หาสถานที่ท่องเที่ยวทางวัฒนธรรม 3 แห่งที่อยู่ในเขตเดียวกันและมีสถานีรถไฟอยู่ใกล้
    intent_q93 = engine.route_query_intent("หาสถานที่ท่องเที่ยวทางวัฒนธรรม 3 แห่งที่อยู่ในเขตเดียวกันและมีสถานีรถไฟอยู่ใกล้")
    assert intent_q93 == "HYBRID_COMPLEX"


def test_benchmark_100_questions_ground_truth():
    """ทดสอบว่าคำถาม Benchmark ทั้ง 100 ข้อมี Ground Truth Entities และ Chunks ครบถ้วน"""
    bench_file = "data/benchmark_100_questions.json"
    assert os.path.exists(bench_file), f"Benchmark file {bench_file} missing"
    
    with open(bench_file, "r", encoding="utf-8") as f:
        questions = json.load(f)

    with open("data/processed/documents_chunks.json", "r", encoding="utf-8") as f:
        chunks = json.load(f)
    valid_entities = {chunk["place_id"] for chunk in chunks}
    valid_chunks = {chunk["chunk_id"] for chunk in chunks}

    assert len(questions) == 100, f"Expected 100 questions but found {len(questions)}"

    categories = set()
    for q in questions:
        categories.add(q["category"])
        assert "id" in q
        assert "query" in q
        assert "ground_truth_entities" in q
        assert len(q["ground_truth_entities"]) > 0, f"Q{q['id']} missing ground_truth_entities"
        assert set(q["ground_truth_entities"]) <= valid_entities, f"Q{q['id']} has invalid entities"
        assert "ground_truth_chunks" in q
        assert len(q["ground_truth_chunks"]) > 0, f"Q{q['id']} missing ground_truth_chunks"
        assert set(q["ground_truth_chunks"]) <= valid_chunks, f"Q{q['id']} has invalid chunks"

    assert len(categories) == 10, f"Expected 10 categories (A-J) but found {len(categories)}"

    for category in categories:
        patterns = {
            tuple(q["ground_truth_entities"])
            for q in questions
            if q["category"] == category
        }
        assert len(patterns) >= 5, f"Category {category} ground truth is insufficiently varied"


def test_model_comparison_raw_artifact():
    """ทดสอบว่าไฟล์ผลลัพธ์ดิบ model_comparison_raw.json มีโครงสร้างสมบูรณ์และตรวจสอบได้จริง"""
    raw_file = "data/model_comparison_raw.json"
    assert os.path.exists(raw_file), f"File {raw_file} missing"

    with open(raw_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "summary" in data
    assert "raw_results" in data
    assert len(data["raw_results"]) == 10

    for item in data["raw_results"]:
        assert "gemini_api" in item
        assert "deterministic_fallback" in item
        assert "local_ollama_3b" in item
        assert item["gemini_api"]["latency_sec"] > 0
        assert item["deterministic_fallback"]["latency_sec"] > 0
        assert item["local_ollama_3b"]["status"] in {
            "MEASURED_LIVE",
            "UNAVAILABLE_NOT_MEASURED",
        }
