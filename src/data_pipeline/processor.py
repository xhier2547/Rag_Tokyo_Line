"""
Data Pipeline Processor Orchestrator
ประมวลผลข้อมูลโตเกียว ตรวจสอบความถูกต้องด้วย Pydantic Models
ทำความสะอาดเนื้อหา แบ่ง Chunks และบันทึกเป็นไฟล์ Structured CSV / JSON
"""
import os
import json
import pandas as pd
from typing import List, Dict, Any

from src.data_pipeline.cleaner import clean_text
from src.data_pipeline.models import (
    PlaceModel,
    StationModel,
    LineModel,
    TransitEdgeModel,
    PlaceStationEdgeModel,
    DocumentChunkModel
)
from src.data_pipeline.chunker import TokyoDocumentChunker
from src.data_pipeline.tokyo_data import (
    PLACES_DATA,
    STATIONS_DATA,
    LINES_DATA,
    TRANSIT_EDGES_DATA,
    PLACE_STATION_EDGES
)

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "processed")

def process_and_export_all(output_dir: str = PROCESSED_DIR) -> Dict[str, Any]:
    """
    ประมวลผลข้อมูลครบทุกมิติและส่งออกเป็นไฟล์ใน data/processed/
    คืนค่าสรุปผลจำนวนข้อมูลที่ประมวลผลได้
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"=== Starting Tokyo Data Pipeline Processing -> [{output_dir}] ===")

    # 1. ประมวลผลและตรวจสอบ Lines
    validated_lines: List[LineModel] = []
    for item in LINES_DATA:
        line_obj = LineModel(
            line_id=item["line_id"],
            name_th=clean_text(item["name_th"]),
            name_en=clean_text(item["name_en"]),
            line_code=item["line_code"],
            operator=clean_text(item["operator"]),
            color=item["color"]
        )
        validated_lines.append(line_obj)
    
    df_lines = pd.DataFrame([l.model_dump() for l in validated_lines])
    lines_csv_path = os.path.join(output_dir, "lines.csv")
    df_lines.to_csv(lines_csv_path, index=False, encoding="utf-8-sig")
    print(f" Saved {len(df_lines)} lines to '{lines_csv_path}'")

    # 2. ประมวลผลและตรวจสอบ Stations
    validated_stations: List[StationModel] = []
    for item in STATIONS_DATA:
        st_obj = StationModel(
            station_id=item["station_id"],
            name_th=clean_text(item["name_th"]),
            name_en=clean_text(item["name_en"]),
            name_ja=clean_text(item["name_ja"]),
            lines=item["lines"],
            ward=item["ward"],
            latitude=float(item["latitude"]),
            longitude=float(item["longitude"])
        )
        validated_stations.append(st_obj)
    
    df_stations = pd.DataFrame([s.model_dump() for s in validated_stations])
    stations_csv_path = os.path.join(output_dir, "stations.csv")
    df_stations.to_csv(stations_csv_path, index=False, encoding="utf-8-sig")
    print(f" Saved {len(df_stations)} stations to '{stations_csv_path}'")

    # 3. ประมวลผลและตรวจสอบ Places
    validated_places: List[PlaceModel] = []
    for item in PLACES_DATA:
        pl_obj = PlaceModel(
            place_id=item["place_id"],
            name_th=clean_text(item["name_th"]),
            name_en=clean_text(item["name_en"]),
            name_ja=clean_text(item["name_ja"]),
            ward=item["ward"],
            category=item["category"],
            latitude=float(item["latitude"]),
            longitude=float(item["longitude"]),
            description_th=clean_text(item["description_th"]),
            description_en=clean_text(item["description_en"]),
            opening_hours=clean_text(item["opening_hours"]),
            admission_fee=clean_text(item["admission_fee"]),
            nearest_station_id=item["nearest_station_id"],
            walk_time_min=int(item["walk_time_min"])
        )
        validated_places.append(pl_obj)
    
    df_places = pd.DataFrame([p.model_dump() for p in validated_places])
    places_csv_path = os.path.join(output_dir, "places.csv")
    df_places.to_csv(places_csv_path, index=False, encoding="utf-8-sig")
    print(f" Saved {len(df_places)} places to '{places_csv_path}'")

    # 4. ประมวลผลและตรวจสอบ Transit Edges (โครงข่ายรถไฟ)
    # เพิ่ม edge ขากลับอัตโนมัติ (Bi-directional graph) เพื่อให้คำนวณเส้นทางได้ทั้งไปและกลับ
    validated_edges: List[TransitEdgeModel] = []
    seen_pairs = set()

    for item in TRANSIT_EDGES_DATA:
        e1 = TransitEdgeModel(
            from_station_id=item["from_station_id"],
            to_station_id=item["to_station_id"],
            line_id=item["line_id"],
            line_name=clean_text(item["line_name"]),
            duration_min=int(item["duration_min"]),
            distance_km=float(item["distance_km"])
        )
        validated_edges.append(e1)
        seen_pairs.add((item["from_station_id"], item["to_station_id"], item["line_id"]))

        # Edge ขากลับ
        rev_pair = (item["to_station_id"], item["from_station_id"], item["line_id"])
        if rev_pair not in seen_pairs:
            e2 = TransitEdgeModel(
                from_station_id=item["to_station_id"],
                to_station_id=item["from_station_id"],
                line_id=item["line_id"],
                line_name=clean_text(item["line_name"]),
                duration_min=int(item["duration_min"]),
                distance_km=float(item["distance_km"])
            )
            validated_edges.append(e2)
            seen_pairs.add(rev_pair)

    df_edges = pd.DataFrame([e.model_dump() for e in validated_edges])
    transit_csv_path = os.path.join(output_dir, "transit_edges.csv")
    df_edges.to_csv(transit_csv_path, index=False, encoding="utf-8-sig")
    print(f" Saved {len(df_edges)} transit network edges to '{transit_csv_path}'")

    # 5. ประมวลผลและตรวจสอบ Place to Station Edges
    validated_ps_edges: List[PlaceStationEdgeModel] = []
    for item in PLACE_STATION_EDGES:
        pse = PlaceStationEdgeModel(
            place_id=item["place_id"],
            station_id=item["station_id"],
            walk_time_min=int(item["walk_time_min"]),
            distance_m=int(item["distance_m"]),
            exit_info=clean_text(item["exit_info"])
        )
        validated_ps_edges.append(pse)

    df_ps_edges = pd.DataFrame([pse.model_dump() for pse in validated_ps_edges])
    ps_csv_path = os.path.join(output_dir, "place_station_edges.csv")
    df_ps_edges.to_csv(ps_csv_path, index=False, encoding="utf-8-sig")
    print(f" Saved {len(df_ps_edges)} place-station edges to '{ps_csv_path}'")

    # 6. ประมวลผล Chunking สำหรับ Vector DB & BM25
    chunker = TokyoDocumentChunker(chunk_size=350, chunk_overlap=70)
    all_chunks: List[DocumentChunkModel] = []
    for place_dict in PLACES_DATA:
        chunks = chunker.chunk_place(place_dict)
        all_chunks.extend(chunks)

    chunks_json_path = os.path.join(output_dir, "documents_chunks.json")
    with open(chunks_json_path, "w", encoding="utf-8") as f:
        json.dump([c.model_dump() for c in all_chunks], f, ensure_ascii=False, indent=2)
    print(f" Saved {len(all_chunks)} document chunks to '{chunks_json_path}'")

    summary = {
        "lines_count": len(df_lines),
        "stations_count": len(df_stations),
        "places_count": len(df_places),
        "transit_edges_count": len(df_edges),
        "place_station_edges_count": len(df_ps_edges),
        "chunks_count": len(all_chunks),
        "output_directory": output_dir
    }
    print("=== Tokyo Data Pipeline Processing Completed Successfully! ===")
    return summary

if __name__ == "__main__":
    process_and_export_all()
