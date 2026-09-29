"""
tests/test_chart_generator.py
=============================
Automated test suite verifying the chart generation script
and the generated image artifacts in reports/charts/
"""

import os
import pytest
from src.evaluation.generate_charts import generate_all_charts, CHARTS_DIR


def test_generate_all_charts_creates_images():
    """
    ทดสอบว่าฟังก์ชัน generate_all_charts สามารถสร้างรูปภาพ PNG ทั้ง 4 รูปได้ถูกต้อง
    และแต่ละไฟล์มีขนาดมากกว่า 10 KB (ไม่ใช่ไฟล์เปล่า)
    """
    generate_all_charts()

    expected_files = [
        "chart_1_embedding_comparison.png",
        "chart_2_llm_latency_throughput.png",
        "chart_3_llm_resource_usage.png",
        "chart_4_category_latency.png"
    ]

    for fname in expected_files:
        fpath = os.path.join(CHARTS_DIR, fname)
        assert os.path.exists(fpath), f"ไม่พบไฟล์รูปภาพที่คาดหวัง: {fpath}"
        fsize = os.path.getsize(fpath)
        assert fsize > 10000, f"ขนาดไฟล์รูปภาพเล็กผิดปกติ ({fsize} bytes): {fname}"


def test_comparison_report_exists():
    """
    ทดสอบว่ามีไฟล์ model_comparison_report.md และมีหัวข้อหลักครบถ้วน
    """
    report_path = os.path.join(os.path.dirname(CHARTS_DIR), "..", "model_comparison_report.md")
    report_path = os.path.abspath(report_path)
    assert os.path.exists(report_path), f"ไม่พบไฟล์รายงาน: {report_path}"

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Embedding" in content
    assert "Gemini 3.1 Flash Lite" in content
    assert "Qwen 2.5 3B" in content
    assert "chart_1_embedding_comparison.png" in content
