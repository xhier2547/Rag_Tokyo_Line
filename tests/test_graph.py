"""
Automated Tests for Graph RAG & Neo4j Pathfinding Engine
ทดสอบการเชื่อมต่อ Neo4j, การสร้างโหนดและเส้นเชื่อม, การคำนวณ Shortest Path,
การวางแผนการเดินทางแบบ End-to-End (เดิน + รถไฟ + เดิน) และการดึง Graph Context
"""
import pytest
from src.graph.connection import Neo4jConnection
from src.graph.builder import TokyoGraphBuilder
from src.graph.pathfinder import TokyoGraphPathfinder

@pytest.fixture(scope="module")
def pathfinder():
    return TokyoGraphPathfinder()

# 1. ทดสอบการเชื่อมต่อ Neo4j
def test_neo4j_connection():
    driver = Neo4jConnection.get_driver()
    # Neo4j is optional by design; NetworkX is the documented offline backend.
    if driver is None:
        graph = TokyoGraphBuilder().build_networkx_graph()
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0
    else:
        assert driver is not None
        with driver.session() as session:
            val = session.run("RETURN 1 AS n").single()["n"]
            assert val == 1

# 2. ทดสอบการสร้างและตรวจสอบขนาดของ Graph
def test_graph_builder_ingestion():
    builder = TokyoGraphBuilder()
    stats = builder.ingest_to_neo4j()
    assert stats["nodes_created"] > 0
    assert stats["relationships_created"] > 0
    assert stats["status"] in ["connected_neo4j", "fallback_cache"]

# 3. ทดสอบการคำนวณเส้นทางรถไฟที่เร็วที่สุด (Shortest Transit Path)
def test_shortest_transit_path(pathfinder):
    res = pathfinder.find_shortest_transit("ST_ASAKUSA", "ST_SHIBUYA")
    assert res["success"] is True
    assert res["total_duration_min"] > 0
    assert len(res["steps"]) >= 1
    assert "สถานีอาซากุสะ" in res["from_station"]
    assert "สถานีชิบูย่า" in res["to_station"]

def test_shortest_transit_same_station(pathfinder):
    res = pathfinder.find_shortest_transit("ST_TOKYO", "ST_TOKYO")
    assert res["success"] is True
    assert res["total_duration_min"] == 0

def test_shortest_transit_invalid_station(pathfinder):
    res = pathfinder.find_shortest_transit("ST_NONEXISTENT", "ST_TOKYO")
    assert res["success"] is False
    assert "ไม่พบสถานี" in res["error"]

# 4. ทดสอบการเดินทางแบบ End-to-End จากสถานที่สู่สถานที่ (Place-to-Place Route)
def test_place_to_place_route(pathfinder):
    # จากวัดเซ็นโซจิ ไปยัง ห้าแยกชิบูย่า
    res = pathfinder.find_place_to_place_route("P_SENSOJI", "P_SHIBUYA_CROSSING")
    assert res["success"] is True
    assert res["total_duration_min"] > 0
    assert res["walk1_min"] == 5   # เซ็นโซจิ -> สถานีอาซากุสะ 5 นาที
    assert res["walk2_min"] == 1   # สถานีชิบูย่า -> ห้าแยกชิบูย่า 1 นาที
    assert len(res["itinerary"]) >= 3

# 5. ทดสอบการค้นหาสถานที่ท่องเที่ยวใกล้สถานี
def test_find_nearby_places(pathfinder):
    # สถานีอาซากุสะ ต้องพบวัดเซ็นโซจิ
    nearby = pathfinder.find_nearby_places("ST_ASAKUSA", max_walk_min=10)
    assert len(nearby) >= 1
    place_ids = [p["place_id"] for p in nearby]
    assert "P_SENSOJI" in place_ids

# 6. ทดสอบการสกัด Graph Context สำหรับส่งให้ LLM
def test_extract_graph_context_route_query(pathfinder):
    query = "อยากเดินทางจากวัดเซ็นโซจิไปชิบูย่าต้องนั่งรถไฟอย่างไร"
    ctx = pathfinder.extract_graph_context_for_rag(query)
    assert "เซ็นโซจิ" in ctx
    assert "ชิบูย่า" in ctx
    assert "นาที" in ctx

def test_extract_graph_context_single_place(pathfinder):
    query = "ขอข้อมูลโตเกียวทาวเวอร์หน่อยครับ"
    ctx = pathfinder.extract_graph_context_for_rag(query)
    assert "โตเกียวทาวเวอร์" in ctx
    assert "สถานีรถไฟที่ใกล้ที่สุด" in ctx
