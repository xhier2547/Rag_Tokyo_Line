"""
tests/test_evaluation.py
========================
Automated Unit Tests สำหรับ Phase 6: Benchmark & Evaluation Module
- ทดสอบการโหลดชุดคำถาม 100 ข้อ (A-J)
- ทดสอบการกรองคำถามตามหมวดหมู่และการสุ่มตัวอย่าง (Sampling)
- ทดสอบการคำนวณเมตริกสรุปสถิติ (Summary Metrics Calculation)
"""

import os
import pytest
from src.evaluation.evaluator import TokyoRAGEvaluator, EvaluationItemResult, BenchmarkSummary
from src.evaluation.create_benchmark_splits import create_splits


def test_load_100_benchmark_questions():
    """ทดสอบว่าชุดคำถาม 100 ข้อถูกจัดเตรียมไว้ครบถ้วนทั้ง 10 หมวดหมู่ (A-J)"""
    evaluator = TokyoRAGEvaluator()
    questions = evaluator.load_benchmark_questions()
    assert len(questions) == 100

    categories = set(q["category"] for q in questions)
    expected_categories = {"A", "B", "C", "D", "E", "F", "G", "H", "I", "J"}
    assert categories == expected_categories


def test_filter_by_category():
    """ทดสอบการกรองคำถามเฉพาะหมวด เช่น หมวด J (Multi-hop Graph RAG)"""
    evaluator = TokyoRAGEvaluator()
    j_questions = evaluator.load_benchmark_questions(category="J")
    assert len(j_questions) == 10
    assert all(q["category"] == "J" for q in j_questions)
    assert all(q["requires_graph"] is True for q in j_questions)


def test_sample_questions():
    """ทดสอบการสุ่มเลือกตัวแทน 10 ข้อ (หมวดละ 1 ข้อ)"""
    evaluator = TokyoRAGEvaluator()
    sample_10 = evaluator.load_benchmark_questions(sample_size=10)
    assert len(sample_10) == 10
    categories = set(q["category"] for q in sample_10)
    assert len(categories) == 10  # ต้องกระจายครบทั้ง 10 หมวด


def test_stratified_dev_test_split():
    dev, test = create_splits()
    assert len(dev) == 60
    assert len(test) == 40
    assert {item["id"] for item in dev}.isdisjoint({item["id"] for item in test})
    for category in "ABCDEFGHIJ":
        assert sum(item["category"] == category for item in dev) == 6
        assert sum(item["category"] == category for item in test) == 4


def test_calculate_summary():
    """ทดสอบการคำนวณสถิติภาพรวมจากรายการผลการทดสอบจำลอง"""
    evaluator = TokyoRAGEvaluator()
    dummy_results = [
        EvaluationItemResult(
            question_id=1,
            category="A",
            category_name="ทั่วไป",
            query="คำถามทดสอบ 1",
            requires_graph=False,
            mode="gemini",
            model_name="gemini-2.5-flash",
            intent_detected="FACT_RETRIEVAL",
            answer="คำตอบ [อ้างอิง: สถานที่ A]",
            citations=["สถานที่ A"],
            has_citations=True,
            citation_count=1,
            graph_used=False,
            latency_sec=1.5,
            is_cached=False,
            success=True
        ),
        EvaluationItemResult(
            question_id=2,
            category="G",
            category_name="เส้นทาง",
            query="คำถามทดสอบ 2",
            requires_graph=True,
            mode="gemini",
            model_name="gemini-2.5-flash",
            intent_detected="ROUTE_TRANSIT",
            answer="เดินทาง [อ้างอิง: สาย Yamanote]",
            citations=["สาย Yamanote"],
            has_citations=True,
            citation_count=1,
            graph_used=True,
            latency_sec=2.5,
            is_cached=False,
            success=True
        )
    ]

    summary = evaluator.calculate_summary(dummy_results, mode="gemini")
    assert isinstance(summary, BenchmarkSummary)
    assert summary.total_evaluated == 2
    assert summary.success_rate_percent == 100.0
    assert summary.citation_rate_percent == 100.0
    assert summary.avg_latency_sec == 2.0  # (1.5 + 2.5) / 2
    assert summary.graph_utilization_percent == 50.0  # 1 จาก 2
    assert "A" in summary.category_breakdown
    assert "G" in summary.category_breakdown
