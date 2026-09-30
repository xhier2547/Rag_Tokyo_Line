"""
tests/test_ablation_error_analysis.py
=====================================
Unit tests สำหรับการวิเคราะห์ Ablation แยกหมวด A-J และ Error Analysis
"""

import os
import pytest
from src.evaluation.category_ablation_analysis import analyze_ablation_and_errors


def test_category_ablation_and_error_analysis():
    """ทดสอบว่าการคำนวณแยกหมวด A-J ครบทั้ง 10 หมวด และมี Error Distribution ครบ"""
    res = analyze_ablation_and_errors()
    
    assert "category_breakdown" in res
    assert "error_analysis" in res
    
    cats = res["category_breakdown"]
    assert len(cats) == 10
    for c in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]:
        assert c in cats
        stat = cats[c]
        assert "dense_only" in stat
        assert "graph_only" in stat
        assert "hybrid_rag" in stat
        assert 0 <= stat["hybrid_rag"]["hit3_pct"] <= 100
        assert 0.0 <= stat["hybrid_rag"]["mrr"] <= 1.0

    errors = res["error_analysis"]
    assert "distribution" in errors
    dist = errors["distribution"]
    assert "GRAPH_COVERAGE_GAP" in dist
    assert "ENTITY_EXTRACTION_FAILURE" in dist
    assert "FUSION_WEIGHT_IMBALANCE" in dist
    assert "DUPLICATE_SYNONYM_CONFUSION" in dist
    assert "UNSTRUCTURED_SEMANTIC_GAP" in dist
