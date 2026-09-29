"""
Neo4j Knowledge Graph Builder & NetworkX In-Memory Cache
ทำหน้าที่โหลดข้อมูลจาก data/processed/ เข้าสู่ Neo4j Graph Database
พร้อมสร้าง NetworkX In-Memory Graph สำรองสำหรับใช้งานแบบ Offline และ Local Pathfinding
"""
import os
import json
import pandas as pd
import networkx as nx
from typing import Dict, Any, Optional

from src.graph.connection import Neo4jConnection

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
GRAPH_CACHE_PATH = os.path.join(PROCESSED_DIR, "graph_cache.json")

class TokyoGraphBuilder:
    """
    คลาสสำหรับสร้างและนำเข้าข้อมูล Knowledge Graph
    """
    def __init__(self, data_dir: str = PROCESSED_DIR):
        self.data_dir = data_dir
        self.lines_file = os.path.join(data_dir, "lines.csv")
        self.stations_file = os.path.join(data_dir, "stations.csv")
        self.places_file = os.path.join(data_dir, "places.csv")
        self.hotels_file = os.path.join(data_dir, "hotels.csv")
        self.transit_file = os.path.join(data_dir, "transit_edges.csv")
        self.ps_edges_file = os.path.join(data_dir, "place_station_edges.csv")

    def build_networkx_graph(self) -> nx.DiGraph:
        """
        สร้าง In-memory Graph ด้วย NetworkX เพื่อใช้คำนวณเส้นทางและเป็น Offline Fallback
        """
        G = nx.DiGraph()

        # 1. โหลด Stations
        if os.path.exists(self.stations_file):
            df_st = pd.read_csv(self.stations_file)
            for _, r in df_st.iterrows():
                G.add_node(
                    r["station_id"],
                    type="Station",
                    name_th=r["name_th"],
                    name_en=r["name_en"],
                    ward=r["ward"],
                    lat=r["latitude"],
                    lon=r["longitude"],
                    lines=r["lines"]
                )

        # 2. โหลด Places
        if os.path.exists(self.places_file):
            df_pl = pd.read_csv(self.places_file)
            for _, r in df_pl.iterrows():
                G.add_node(
                    r["place_id"],
                    type="Place",
                    name_th=r["name_th"],
                    name_en=r["name_en"],
                    ward=r["ward"],
                    category=r["category"],
                    lat=r["latitude"],
                    lon=r["longitude"],
                    nearest_station_id=r["nearest_station_id"],
                    walk_time_min=r["walk_time_min"],
                    opening_hours=r["opening_hours"],
                    admission_fee=r["admission_fee"]
                )

        # 3. โหลด Transit Edges (Station <-> Station)
        if os.path.exists(self.transit_file):
            df_tr = pd.read_csv(self.transit_file)
            for _, r in df_tr.iterrows():
                G.add_edge(
                    r["from_station_id"],
                    r["to_station_id"],
                    relation="CONNECTED_TO",
                    line_id=r["line_id"],
                    line_name=r["line_name"],
                    weight=float(r["duration_min"]),  # ใช้เวลาเป็น weight สำหรับ Dijkstra
                    duration_min=int(r["duration_min"]),
                    distance_km=float(r["distance_km"])
                )

        # 4. โหลด Place <-> Station Edges (เดินเท้า)
        if os.path.exists(self.ps_edges_file):
            df_ps = pd.read_csv(self.ps_edges_file)
            for _, r in df_ps.iterrows():
                # เชื่อมทั้งสองฝั่ง (เดินจากที่เที่ยวไปสถานี และจากสถานีไปที่เที่ยว)
                G.add_edge(
                    r["place_id"],
                    r["station_id"],
                    relation="NEAR_STATION",
                    weight=float(r["walk_time_min"]),
                    walk_time_min=int(r["walk_time_min"]),
                    distance_m=int(r["distance_m"]),
                    exit_info=r["exit_info"]
                )
                G.add_edge(
                    r["station_id"],
                    r["place_id"],
                    relation="NEAR_PLACE",
                    weight=float(r["walk_time_min"]),
                    walk_time_min=int(r["walk_time_min"]),
                    distance_m=int(r["distance_m"]),
                    exit_info=r["exit_info"]
                )

        # 5. โหลด Hotels (โรงแรมและที่พัก)
        if os.path.exists(self.hotels_file):
            df_ht = pd.read_csv(self.hotels_file)
            for _, r in df_ht.iterrows():
                G.add_node(
                    r["hotel_id"],
                    type="Hotel",
                    name_th=r["name_th"],
                    name_en=r["name_en"],
                    ward=r["ward"],
                    tier=r["tier"],
                    price_range=r["price_range"],
                    nearest_station_id=r["nearest_station_id"],
                    walk_time_min=r["walk_time_min"],
                    highlights=r["highlights"]
                )
                G.add_edge(
                    r["hotel_id"],
                    r["nearest_station_id"],
                    relation="NEAR_STATION",
                    weight=float(r["walk_time_min"]),
                    walk_time_min=int(r["walk_time_min"])
                )
                G.add_edge(
                    r["nearest_station_id"],
                    r["hotel_id"],
                    relation="NEAR_HOTEL",
                    weight=float(r["walk_time_min"]),
                    walk_time_min=int(r["walk_time_min"])
                )

        return G

    def save_graph_cache(self, G: nx.DiGraph, output_file: str = GRAPH_CACHE_PATH):
        """บันทึกข้อมูลกราฟลงไฟล์ JSON Cache สำหรับโหลดเร็ว"""
        cache_data = {
            "nodes": {n: G.nodes[n] for n in G.nodes()},
            "edges": [
                {
                    "from": u,
                    "to": v,
                    **G.edges[u, v]
                }
                for u, v in G.edges()
            ]
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f" Saved Graph Cache to '{output_file}' ({len(cache_data['nodes'])} nodes, {len(cache_data['edges'])} edges)")

    def ingest_to_neo4j(self) -> Dict[str, Any]:
        """
        นำเข้าข้อมูลทั้งหมดเข้าสู่ Neo4j Graph Database ผ่าน Cypher (Idempotent MERGE)
        """
        driver = Neo4jConnection.get_driver()
        stats = {"status": "offline", "nodes_created": 0, "relationships_created": 0}

        # 1. สร้าง In-memory Graph เสมอเพื่อเป็น Fallback
        G = self.build_networkx_graph()
        self.save_graph_cache(G)

        if not driver:
            print("[TokyoGraphBuilder] Neo4j is offline or unavailable. Using NetworkX Cache.")
            stats["status"] = "fallback_cache"
            stats["nodes_created"] = len(G.nodes())
            stats["relationships_created"] = len(G.edges())
            return stats

        print("[TokyoGraphBuilder] Ingesting Tokyo Tourism & Transit Knowledge Graph to Neo4j...")
        with driver.session() as session:
            # สร้าง Indexes และ Constraints เพื่อความเร็วในการ Query
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Place) REQUIRE p.place_id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Station) REQUIRE s.station_id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (l:Line) REQUIRE l.line_id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (h:Hotel) REQUIRE h.hotel_id IS UNIQUE")

            # 1. Ingest Lines
            df_lines = pd.read_csv(self.lines_file)
            for _, r in df_lines.iterrows():
                session.run(
                    """
                    MERGE (l:Line {line_id: $line_id})
                    SET l.name_th = $name_th,
                        l.name_en = $name_en,
                        l.line_code = $line_code,
                        l.operator = $operator,
                        l.color = $color
                    """,
                    line_id=r["line_id"],
                    name_th=r["name_th"],
                    name_en=r["name_en"],
                    line_code=r["line_code"],
                    operator=r["operator"],
                    color=r["color"]
                )

            # 2. Ingest Stations & Connect to Lines
            df_stations = pd.read_csv(self.stations_file)
            for _, r in df_stations.iterrows():
                session.run(
                    """
                    MERGE (s:Station {station_id: $station_id})
                    SET s.name_th = $name_th,
                        s.name_en = $name_en,
                        s.name_ja = $name_ja,
                        s.ward = $ward,
                        s.latitude = $lat,
                        s.longitude = $lon
                    MERGE (w:Ward {name: $ward})
                    MERGE (s)-[:LOCATED_IN]->(w)
                    """,
                    station_id=r["station_id"],
                    name_th=r["name_th"],
                    name_en=r["name_en"],
                    name_ja=r["name_ja"],
                    ward=r["ward"],
                    lat=float(r["latitude"]),
                    lon=float(r["longitude"])
                )
                # เชื่อม Station เข้ากับ Line
                lines_list = str(r["lines"]).split(";")
                for lid in lines_list:
                    if lid.strip():
                        session.run(
                            """
                            MATCH (s:Station {station_id: $station_id})
                            MATCH (l:Line {line_id: $line_id})
                            MERGE (s)-[:ON_LINE]->(l)
                            """,
                            station_id=r["station_id"],
                            line_id=lid.strip()
                        )

            # 3. Ingest Places
            df_places = pd.read_csv(self.places_file)
            for _, r in df_places.iterrows():
                session.run(
                    """
                    MERGE (p:Place {place_id: $place_id})
                    SET p.name_th = $name_th,
                        p.name_en = $name_en,
                        p.name_ja = $name_ja,
                        p.ward = $ward,
                        p.category = $category,
                        p.latitude = $lat,
                        p.longitude = $lon,
                        p.description_th = $description_th,
                        p.description_en = $description_en,
                        p.opening_hours = $opening_hours,
                        p.admission_fee = $admission_fee,
                        p.walk_time_min = $walk_time_min
                    MERGE (w:Ward {name: $ward})
                    MERGE (p)-[:LOCATED_IN]->(w)
                    MERGE (c:Category {name: $category})
                    MERGE (p)-[:HAS_CATEGORY]->(c)
                    """,
                    place_id=r["place_id"],
                    name_th=r["name_th"],
                    name_en=r["name_en"],
                    name_ja=r["name_ja"],
                    ward=r["ward"],
                    category=r["category"],
                    lat=float(r["latitude"]),
                    lon=float(r["longitude"]),
                    description_th=r["description_th"],
                    description_en=r["description_en"],
                    opening_hours=r["opening_hours"],
                    admission_fee=r["admission_fee"],
                    walk_time_min=int(r["walk_time_min"])
                )

            # 4. Ingest Transit Edges
            df_transit = pd.read_csv(self.transit_file)
            for _, r in df_transit.iterrows():
                session.run(
                    """
                    MATCH (s1:Station {station_id: $from_id})
                    MATCH (s2:Station {station_id: $to_id})
                    MERGE (s1)-[rel:CONNECTED_TO {line_id: $line_id}]->(s2)
                    SET rel.duration_min = $duration_min,
                        rel.distance_km = $distance_km,
                        rel.line_name = $line_name
                    """,
                    from_id=r["from_station_id"],
                    to_id=r["to_station_id"],
                    line_id=r["line_id"],
                    line_name=r["line_name"],
                    duration_min=int(r["duration_min"]),
                    distance_km=float(r["distance_km"])
                )

            # 5. Ingest Place-Station Walking Edges
            df_ps = pd.read_csv(self.ps_edges_file)
            for _, r in df_ps.iterrows():
                session.run(
                    """
                    MATCH (p:Place {place_id: $place_id})
                    MATCH (s:Station {station_id: $station_id})
                    MERGE (p)-[rel:NEAR_STATION]->(s)
                    SET rel.walk_min = $walk_min,
                        rel.distance_m = $distance_m,
                        rel.exit_info = $exit_info
                    MERGE (s)-[rel2:NEAR_PLACE]->(p)
                    SET rel2.walk_min = $walk_min,
                        rel2.distance_m = $distance_m,
                        rel2.exit_info = $exit_info
                    """,
                    place_id=r["place_id"],
                    station_id=r["station_id"],
                    walk_min=int(r["walk_time_min"]),
                    distance_m=int(r["distance_m"]),
                    exit_info=r["exit_info"]
                )

            # 6. Ingest Hotels
            if os.path.exists(self.hotels_file):
                df_hotels = pd.read_csv(self.hotels_file)
                for _, r in df_hotels.iterrows():
                    session.run(
                        """
                        MERGE (h:Hotel {hotel_id: $hotel_id})
                        SET h.name_th = $name_th,
                            h.name_en = $name_en,
                            h.ward = $ward,
                            h.tier = $tier,
                            h.price_range = $price_range,
                            h.highlights = $highlights,
                            h.description_th = $description_th
                        WITH h
                        MATCH (s:Station {station_id: $station_id})
                        MERGE (h)-[r1:NEAR_STATION]->(s)
                        SET r1.walk_min = $walk_time_min
                        MERGE (s)-[r2:NEAR_HOTEL]->(h)
                        SET r2.walk_min = $walk_time_min
                        """,
                        hotel_id=r["hotel_id"],
                        name_th=r["name_th"],
                        name_en=r["name_en"],
                        ward=r["ward"],
                        tier=r["tier"],
                        price_range=r["price_range"],
                        highlights=r["highlights"],
                        description_th=r["description_th"],
                        station_id=r["nearest_station_id"],
                        walk_time_min=int(r["walk_time_min"])
                    )

            # ตรวจสอบจำนวนโหนดและความสัมพันธ์ในฐานข้อมูล
            node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
            print(f"[TokyoGraphBuilder] Successfully ingested into Neo4j! Total Nodes: {node_count}, Total Relationships: {rel_count}")

            stats["status"] = "connected_neo4j"
            stats["nodes_created"] = node_count
            stats["relationships_created"] = rel_count

        return stats

if __name__ == "__main__":
    builder = TokyoGraphBuilder()
    builder.ingest_to_neo4j()
