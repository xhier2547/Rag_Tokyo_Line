"""
Automated Unit Tests for Tokyo Data Pipeline
ทดสอบความถูกต้องของการทำความสะอาดข้อความ, การแบ่ง Chunk,
การตรวจสอบ Schema ด้วย Pydantic และความสมบูรณ์ของไฟล์ข้อมูลใน data/processed/
"""
import os
import json
import pytest
import pandas as pd
from pydantic import ValidationError

from src.data_pipeline.cleaner import clean_text, normalize_station_name
from src.data_pipeline.models import (
    PlaceModel,
    StationModel,
    LineModel,
    TransitEdgeModel,
    PlaceStationEdgeModel,
    DocumentChunkModel
)
from src.data_pipeline.chunker import TokyoDocumentChunker
from src.data_pipeline.processor import process_and_export_all

# 1. ทดสอบฟังก์ชันทำความสะอาดข้อความ
def test_clean_text():
    # ทดสอบการแก้ไขสระอำเพี้ยน
    corrupted_thai = "น\ufffd\u0e32เสนอ ข้อมูล"
    cleaned = clean_text(corrupted_thai)
    assert "นำเสนอ" in cleaned or "นาเสนอ" in cleaned
    
    # ทดสอบการตัดช่องว่างซ้ำซ้อน
    spaced_text = "  วัดเซ็นโซจิ    อาซากุสะ \t\t โตเกียว  "
    assert clean_text(spaced_text) == "วัดเซ็นโซจิ อาซากุสะ โตเกียว"
    
    # ทดสอบค่าว่าง
    assert clean_text("") == ""
    assert clean_text(None) == ""

def test_normalize_station_name():
    assert normalize_station_name("Shinjuku Station") == "Shinjuku"
    assert normalize_station_name("สถานีชิบูย่า") == "ชิบูย่า"
    assert normalize_station_name("東京駅") == "東京"

# 2. ทดสอบ Pydantic Data Models Validation
def test_place_model_valid():
    valid_place = PlaceModel(
        place_id="P_TEST",
        name_th="สถานที่ทดสอบ",
        name_en="Test Place",
        name_ja="テスト",
        ward="Shibuya",
        category="Landmark",
        latitude=35.65,
        longitude=139.70,
        description_th="รายละเอียดทดสอบ",
        description_en="Test description",
        opening_hours="09:00 - 18:00",
        admission_fee="ฟรี",
        nearest_station_id="ST_TEST",
        walk_time_min=5
    )
    assert valid_place.place_id == "P_TEST"
    assert valid_place.walk_time_min == 5

def test_place_model_invalid_coords():
    # ละติจูดนอกโตเกียวต้องเกิด ValidationError
    with pytest.raises(ValidationError):
        PlaceModel(
            place_id="P_FAIL",
            name_th="พิกัดผิด",
            name_en="Invalid Coords",
            name_ja="エラー",
            ward="Taito",
            category="Temple",
            latitude=13.75,  # กรุงเทพฯ ไม่ใช่โตเกียว
            longitude=100.50,
            description_th="ทดสอบ",
            description_en="Test",
            opening_hours="24h",
            admission_fee="Free",
            nearest_station_id="ST_TEST",
            walk_time_min=2
        )

# 3. ทดสอบการทำงานของ Document Chunker
def test_chunker_output_and_metadata():
    chunker = TokyoDocumentChunker(chunk_size=100, chunk_overlap=20)
    sample_place = {
        "place_id": "P_SAMPLE",
        "name_th": "ศาลเจ้าตัวอย่าง",
        "name_en": "Sample Shrine",
        "name_ja": "神社",
        "ward": "Chiyoda",
        "category": "Temple & Shrine",
        "latitude": 35.69,
        "longitude": 139.75,
        "description_th": "ศาลเจ้าเก่าแก่ที่มีประวัติศาสตร์ยาวนานกว่า 400 ปีในกรุงโตเกียว บรรยากาศเงียบสงบร่มรื่น รายล้อมด้วยต้นไม้ใหญ่",
        "description_en": "An ancient shrine with over 400 years of history in Tokyo.",
        "opening_hours": "08:00 - 17:00",
        "admission_fee": "เข้าชมฟรี",
        "nearest_station_id": "ST_TOKYO",
        "walk_time_min": 7
    }
    chunks = chunker.chunk_place(sample_place)
    assert len(chunks) >= 2  # ต้องมีอย่างน้อย chunk เนื้อหา + chunk ข้อมูลการเดินทาง
    
    # ตรวจสอบ chunk ข้อมูลการเดินทาง
    info_chunk = [c for c in chunks if c.chunk_id.endswith("_INFO")][0]
    assert "ST_TOKYO" in info_chunk.nearest_station
    assert info_chunk.walk_time_min == 7
    assert "เข้าชมฟรี" in info_chunk.content_th

# 4. ทดสอบความครบถ้วนสมบูรณ์ของไฟล์ข้อมูลหลัง Pipeline รัน
def test_processed_files_exist_and_valid():
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")
    summary = process_and_export_all(output_dir)

    assert summary["places_count"] >= 10
    assert summary["stations_count"] >= 15
    assert summary["lines_count"] >= 8
    assert summary["transit_edges_count"] >= 30
    assert summary["chunks_count"] >= 20

    # ตรวจสอบการอ่านไฟล์ CSV
    df_places = pd.read_csv(os.path.join(output_dir, "places.csv"))
    df_stations = pd.read_csv(os.path.join(output_dir, "stations.csv"))
    df_edges = pd.read_csv(os.path.join(output_dir, "transit_edges.csv"))

    assert not df_places.empty
    assert not df_stations.empty
    assert not df_edges.empty

    # ตรวจสอบว่าทุกสถานที่เชื่อมต่อกับสถานีที่มีอยู่จริงใน stations.csv
    valid_station_ids = set(df_stations["station_id"])
    for st_id in df_places["nearest_station_id"]:
        assert st_id in valid_station_ids, f"Station {st_id} not found in stations table"

    # ตรวจสอบไฟล์ chunks json
    with open(os.path.join(output_dir, "documents_chunks.json"), "r", encoding="utf-8") as f:
        chunks_json = json.load(f)
    assert isinstance(chunks_json, list)
    assert len(chunks_json) == summary["chunks_count"]
