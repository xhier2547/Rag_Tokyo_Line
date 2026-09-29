"""
Graph RAG & Cypher Pathfinding Engine
ระบบค้นหาเส้นทาง คำนวณเวลาเดินทาง และวิเคราะห์ความสัมพันธ์เชิงพื้นที่
รองรับทั้ง Cypher Query บน Neo4j และ In-Memory NetworkX Fallback
"""
import re
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from typing import Dict, List, Any, Optional, Tuple
import networkx as nx

from src.graph.connection import Neo4jConnection
from src.graph.builder import TokyoGraphBuilder

class TokyoGraphPathfinder:
    """
    เครื่องมือวิเคราะห์และค้นหาเส้นทางบน Knowledge Graph สำหรับโตเกียว
    """
    def __init__(self):
        self.builder = TokyoGraphBuilder()
        # โหลด NetworkX Graph ไว้เสมอเพื่อความเร็วและเป็น Fallback
        self.nx_graph: nx.DiGraph = self.builder.build_networkx_graph()

    def _resolve_station_id(self, query_name: str) -> Optional[str]:
        """แปลงชื่อสถานี (ไทย/อังกฤษ/รหัส) เป็น station_id ที่ถูกต้อง"""
        q = query_name.lower().strip()
        q = re.sub(r'สถานี|station|駅', '', q).strip()

        for node, data in self.nx_graph.nodes(data=True):
            if data.get("type") == "Station":
                if node.lower() == q or data.get("name_en", "").lower() == q or data.get("name_th", "").lower() == q:
                    return node
                # partial matching
                if q in data.get("name_en", "").lower() or q in data.get("name_th", "").lower() or q in node.lower():
                    return node
        return None

    def _resolve_place_id(self, query_name: str) -> Optional[str]:
        """แปลงชื่อสถานที่ (ไทย/อังกฤษ/รหัส) เป็น place_id ที่ถูกต้อง"""
        q = query_name.lower().strip()
        q = re.sub(r'วัด|สวน|ตลาด|หอคอย|ห้าง|ศาลเจ้า|temple|shrine|park|tower|market', '', q).strip()

        for node, data in self.nx_graph.nodes(data=True):
            if data.get("type") == "Place":
                if node.lower() == q or data.get("name_en", "").lower() == q or data.get("name_th", "").lower() == q:
                    return node
                if q in data.get("name_en", "").lower() or q in data.get("name_th", "").lower() or q in node.lower():
                    return node
        return None

    def find_shortest_transit(self, from_station: str, to_station: str) -> Dict[str, Any]:
        """
        คำนวณเส้นทางรถไฟที่เร็วที่สุดระหว่าง 2 สถานี
        คืนค่า: ลำดับสถานี, สายรถไฟ, เวลาเดินทางรวม (นาที) และระยะทางรวม
        """
        st1 = self._resolve_station_id(from_station)
        st2 = self._resolve_station_id(to_station)

        if not st1 or not st2:
            return {
                "success": False,
                "error": f"ไม่พบสถานีต้นทาง ({from_station}) หรือปลายทาง ({to_station}) ในฐานข้อมูล"
            }

        if st1 == st2:
            st_data = self.nx_graph.nodes[st1]
            return {
                "success": True,
                "from_station": st_data.get("name_th", st1),
                "to_station": st_data.get("name_th", st2),
                "total_duration_min": 0,
                "total_distance_km": 0.0,
                "steps": ["สถานีเดียวกัน ไม่ต้องเดินทางด้วยรถไฟ"]
            }

        # 1. พยายามค้นหาผ่าน Neo4j ก่อน
        driver = Neo4jConnection.get_driver()
        if driver:
            try:
                with driver.session() as session:
                    cypher = """
                    MATCH (start:Station {station_id: $from_id})
                    MATCH (target:Station {station_id: $to_id})
                    MATCH p = shortestPath((start)-[:CONNECTED_TO*]-(target))
                    RETURN [n IN nodes(p) | n.name_th] AS station_names,
                           [r IN relationships(p) | r.line_name] AS line_names,
                           [r IN relationships(p) | r.duration_min] AS durations,
                           [r IN relationships(p) | r.distance_km] AS distances
                    """
                    result = session.run(cypher, from_id=st1, to_id=st2).single()
                    if result and result["station_names"]:
                        stations = result["station_names"]
                        lines = result["line_names"]
                        durations = [int(d) for d in result["durations"]]
                        distances = [float(d) for d in result["distances"]]
                        
                        steps = []
                        for i in range(len(lines)):
                            steps.append(
                                f"นั่งรถไฟ {lines[i]} จาก {stations[i]} ไปยัง {stations[i+1]} (ใช้เวลา {durations[i]} นาที)"
                            )

                        return {
                            "success": True,
                            "engine": "Neo4j Cypher",
                            "from_station": stations[0],
                            "to_station": stations[-1],
                            "path": stations,
                            "lines_used": list(set(lines)),
                            "total_duration_min": sum(durations),
                            "total_distance_km": round(sum(distances), 2),
                            "steps": steps
                        }
            except Exception as e:
                print(f"[TokyoGraphPathfinder] Neo4j Cypher shortestPath warning: {e}. Falling back to NetworkX.")

        # 2. NetworkX Dijkstra Fallback
        try:
            # สร้าง Subgraph ที่มีเฉพาะ Station กับ Station
            transit_subgraph = nx.DiGraph()
            for u, v, data in self.nx_graph.edges(data=True):
                if data.get("relation") == "CONNECTED_TO":
                    transit_subgraph.add_edge(u, v, **data)

            path_nodes = nx.dijkstra_path(transit_subgraph, st1, st2, weight="weight")
            total_duration = 0
            total_distance = 0.0
            steps = []
            lines_used = []

            for i in range(len(path_nodes) - 1):
                u = path_nodes[i]
                v = path_nodes[i+1]
                edge_data = transit_subgraph[u][v]
                u_name = self.nx_graph.nodes[u].get("name_th", u)
                v_name = self.nx_graph.nodes[v].get("name_th", v)
                dur = edge_data.get("duration_min", 0)
                dist = edge_data.get("distance_km", 0.0)
                line_name = edge_data.get("line_name", "รถไฟสายหลัก")

                total_duration += dur
                total_distance += dist
                lines_used.append(line_name)
                steps.append(f"นั่งรถไฟ {line_name} จาก {u_name} ไปยัง {v_name} (ใช้เวลา {dur} นาที)")

            return {
                "success": True,
                "engine": "NetworkX Dijkstra Fallback",
                "from_station": self.nx_graph.nodes[st1].get("name_th", st1),
                "to_station": self.nx_graph.nodes[st2].get("name_th", st2),
                "path": [self.nx_graph.nodes[n].get("name_th", n) for n in path_nodes],
                "lines_used": list(set(lines_used)),
                "total_duration_min": total_duration,
                "total_distance_km": round(total_distance, 2),
                "steps": steps
            }
        except Exception as ex:
            return {"success": False, "error": f"ไม่พบเส้นทางเชื่อมต่อ: {ex}"}

    def find_place_to_place_route(self, from_place: str, to_place: str) -> Dict[str, Any]:
        """
        คำนวณการเดินทางแบบ End-to-End จากสถานที่หนึ่งไปยังอีกสถานที่หนึ่ง
        (เดินเท้า -> รถไฟ -> เดินเท้า)
        """
        p1 = self._resolve_place_id(from_place)
        p2 = self._resolve_place_id(to_place)

        if not p1 or not p2:
            return {
                "success": False,
                "error": f"ไม่พบสถานที่ต้นทาง ({from_place}) หรือปลายทาง ({to_place})"
            }

        p1_data = self.nx_graph.nodes[p1]
        p2_data = self.nx_graph.nodes[p2]

        st1_id = p1_data.get("nearest_station_id")
        st2_id = p2_data.get("nearest_station_id")

        walk1_min = int(p1_data.get("walk_time_min", 0))
        walk2_min = int(p2_data.get("walk_time_min", 0))

        # หากเป็นสถานที่ที่อยู่ใกล้สถานีเดียวกัน
        if st1_id == st2_id:
            st_name = self.nx_graph.nodes[st1_id].get("name_th", st1_id)
            return {
                "success": True,
                "from_place": p1_data["name_th"],
                "to_place": p2_data["name_th"],
                "same_station": True,
                "nearest_station": st_name,
                "total_duration_min": walk1_min + walk2_min,
                "itinerary": [
                    f"1. เดินจาก {p1_data['name_th']} ไปยังสถานี {st_name} (ใช้เวลาประมาณ {walk1_min} นาที)",
                    f"2. เดินต่อจากสถานี {st_name} ไปยัง {p2_data['name_th']} (ใช้เวลาประมาณ {walk2_min} นาที)",
                    f"รวมเวลาเดินเท้าประมาณ {walk1_min + walk2_min} นาที (อยู่ในย่านเดียวกัน)"
                ]
            }

        # คำนวณเส้นทางรถไฟระหว่าง Station 1 -> Station 2
        transit_res = self.find_shortest_transit(st1_id, st2_id)
        if not transit_res.get("success"):
            return transit_res

        total_time = walk1_min + transit_res["total_duration_min"] + walk2_min
        st1_name = self.nx_graph.nodes[st1_id].get("name_th", st1_id)
        st2_name = self.nx_graph.nodes[st2_id].get("name_th", st2_id)

        itinerary = [
            f"1. เดินเท้าจาก {p1_data['name_th']} ไปยังสถานี {st1_name} (ประมาณ {walk1_min} นาที)",
            *transit_res["steps"],
            f"3. ออกจากสถานี {st2_name} เดินเท้าต่อไปยัง {p2_data['name_th']} (ประมาณ {walk2_min} นาที)"
        ]

        return {
            "success": True,
            "from_place": p1_data["name_th"],
            "to_place": p2_data["name_th"],
            "from_station": st1_name,
            "to_station": st2_name,
            "walk1_min": walk1_min,
            "transit_min": transit_res["total_duration_min"],
            "walk2_min": walk2_min,
            "total_duration_min": total_time,
            "lines_used": transit_res["lines_used"],
            "itinerary": itinerary
        }

    def find_nearby_places(self, station_query: str, max_walk_min: int = 15) -> List[Dict[str, Any]]:
        """ค้นหาสถานที่ท่องเที่ยวที่อยู่ใกล้สถานีรถไฟ"""
        st_id = self._resolve_station_id(station_query)
        if not st_id:
            return []

        results = []
        for u, v, data in self.nx_graph.edges(st_id, data=True):
            if data.get("relation") == "NEAR_PLACE":
                p_data = self.nx_graph.nodes[v]
                walk_min = data.get("walk_time_min", 999)
                if walk_min <= max_walk_min:
                    results.append({
                        "place_id": v,
                        "name_th": p_data.get("name_th"),
                        "name_en": p_data.get("name_en"),
                        "category": p_data.get("category"),
                        "ward": p_data.get("ward"),
                        "walk_time_min": walk_min,
                        "exit_info": data.get("exit_info", "")
                    })
        results.sort(key=lambda x: x["walk_time_min"])
        return results

    def find_neighboring_attractions(self, station_query: str, max_transit_min: int = 15) -> List[Dict[str, Any]]:
        """
        ค้นหาสถานที่ท่องเที่ยวจากสถานีต้นทาง ทั้งที่เดินถึงได้โดยตรง และที่นั่งรถไฟต่อไปได้ใน 1-2 สถานี (ไม่เกิน max_transit_min นาที)
        ช่วยตอบโจทย์คำถามเช่น "อยู่ที่ชิบูย่า จะไปเที่ยวไหนดี" โดยเน้นย่านข้างเคียงที่เดินทางสะดวก ไม่หลุดออกนอกกรอบ
        """
        st_id = self._resolve_station_id(station_query)
        if not st_id:
            return []

        results = []
        origin_st_name = self.nx_graph.nodes[st_id].get("name_th", st_id)

        # 1. สถานที่ที่เดินถึงได้โดยตรงที่สถานีนี้
        direct_places = self.find_nearby_places(st_id)
        for dp in direct_places:
            results.append({
                **dp,
                "transit_type": "direct_walk",
                "station_from": origin_st_name,
                "transit_desc": f"อยู่ที่สถานีนี้ {origin_st_name} (เดินเท้า ~{dp['walk_time_min']} นาที)",
                "total_time_min": dp["walk_time_min"]
            })

        # 2. สถานที่ในสถานีข้างเคียง (เชื่อมต่อทางรถไฟ 1-2 สถานี)
        for u, v, data in self.nx_graph.edges(st_id, data=True):
            if data.get("relation") == "CONNECTED_TO":
                neighbor_st = v
                neighbor_name = self.nx_graph.nodes[v].get("name_th", v)
                line_name = data.get("line_name", "")
                transit_min = data.get("duration_min", 0)

                neighbor_places = self.find_nearby_places(neighbor_st)
                for np in neighbor_places:
                    total_t = transit_min + np["walk_time_min"]
                    if total_t <= max_transit_min:
                        results.append({
                            **np,
                            "transit_type": "neighbor_station",
                            "station_name": neighbor_name,
                            "line_name": line_name,
                            "transit_min": transit_min,
                            "transit_desc": f"นั่ง {line_name} ไป {neighbor_name} ({transit_min} นาที) แล้วเดิน ~{np['walk_time_min']} นาที",
                            "total_time_min": total_t
                        })

        results.sort(key=lambda x: x["total_time_min"])
        return results

    def extract_graph_context_for_rag(self, query: str) -> str:
        """
        ฟังก์ชันหัวใจของ Graph RAG:
        ตรวจจับ Entity และดึงข้อเท็จจริงโครงข่ายความสัมพันธ์เพื่อสร้าง Context ให้ LLM
        """
        clean_q = query.lower()
        context_parts = []

        # 1. ตรวจจับว่ามีการถามเส้นทางระหว่างจุด A -> จุด B หรือไม่
        detected_places = []
        for node, data in self.nx_graph.nodes(data=True):
            if data.get("type") == "Place":
                n_th = data.get("name_th", "").lower()
                n_en = data.get("name_en", "").lower()
                # ตรวจชื่อหลัก
                key_th = n_th.split("(")[0].strip()
                if key_th in clean_q or n_en in clean_q:
                    detected_places.append((node, data["name_th"]))

        detected_stations = []
        for node, data in self.nx_graph.nodes(data=True):
            if data.get("type") == "Station":
                s_th = re.sub(r'สถานี', '', data.get("name_th", "")).lower()
                s_en = re.sub(r'station', '', data.get("name_en", ""), flags=re.I).lower().strip()
                if (s_th in clean_q and len(s_th) >= 3) or (s_en in clean_q and len(s_en) >= 4):
                    detected_stations.append((node, data["name_th"]))

        # ถ้าพบสถานที่ 2 แห่ง -> คำนวณเส้นทาง Place-to-Place
        if len(detected_places) >= 2:
            p1, p2 = detected_places[0][0], detected_places[1][0]
            route = self.find_place_to_place_route(p1, p2)
            if route.get("success"):
                context_parts.append(
                    f"[ข้อมูลเส้นทางและเวลาเดินทางจาก Knowledge Graph]:\n"
                    f"การเดินทางจาก '{route['from_place']}' ไปยัง '{route['to_place']}':\n"
                    + "\n".join(route["itinerary"]) + "\n"
                    f"รวมระยะเวลาเดินทางทั้งสิ้น: {route['total_duration_min']} นาที "
                    f"(สายรถไฟที่ใช้: {', '.join(route.get('lines_used', []))})"
                )

        # ถ้าพบสถานี 2 แห่ง -> คำนวณเส้นทาง Station-to-Station
        elif len(detected_stations) >= 2 and any(k in clean_q for k in ["ไป", "เดินทาง", "นั่งรถไฟ", "เส้นทาง", "สายอะไร"]):
            s1, s2 = detected_stations[0][0], detected_stations[1][0]
            route = self.find_shortest_transit(s1, s2)
            if route.get("success"):
                context_parts.append(
                    f"[ข้อมูลเส้นทางรถไฟจาก Knowledge Graph]:\n"
                    f"จากสถานี {route['from_station']} ไปยัง {route['to_station']}:\n"
                    + "\n".join(route["steps"]) + "\n"
                    f"เวลารถไฟรวม: {route['total_duration_min']} นาที "
                    f"ระยะทาง: {route['total_distance_km']} กม. "
                    f"(สายรถไฟ: {', '.join(route['lines_used'])})"
                )

        # ถ้าพบ 1 สถานที่ และ 1 สถานี และมีคำถามเกี่ยวกับการเดินทาง -> คำนวณเส้นทางระหว่าง Place กับ Station
        elif len(detected_places) == 1 and len(detected_stations) == 1 and any(k in clean_q for k in ["ไป", "เดินทาง", "นั่งรถไฟ", "เส้นทาง", "สายอะไร", "จาก"]):
            p_id, p_name = detected_places[0]
            s_id, s_name = detected_stations[0]
            p_data = self.nx_graph.nodes[p_id]
            st_origin_id = p_data.get("nearest_station_id")
            st_origin_name = self.nx_graph.nodes[st_origin_id].get("name_th", st_origin_id)
            walk_min = p_data.get("walk_time_min", 0)

            transit_res = self.find_shortest_transit(st_origin_id, s_id)
            if transit_res.get("success"):
                total_min = walk_min + transit_res["total_duration_min"]
                itinerary = [
                    f"1. เดินเท้าจาก {p_name} ไปยังสถานี {st_origin_name} (ประมาณ {walk_min} นาที)",
                    *transit_res["steps"],
                    f"รวมเวลาเดินทางทั้งหมดถึงสถานี {s_name} ประมาณ {total_min} นาที"
                ]
                context_parts.append(
                    f"[ข้อมูลเส้นทางและการเดินทางจาก Knowledge Graph]:\n"
                    f"การเดินทางจาก '{p_name}' ไปยัง '{s_name}':\n"
                    + "\n".join(itinerary) + "\n"
                    f"(สายรถไฟที่ใช้: {', '.join(transit_res.get('lines_used', []))})"
                )

        # ถ้าพบสถานที่ 1 แห่ง -> ดึงข้อมูลสถานีใกล้เคียงและการเชื่อมโยง
        elif len(detected_places) == 1:
            p_id, p_name = detected_places[0]
            p_data = self.nx_graph.nodes[p_id]
            st_id = p_data.get("nearest_station_id")
            st_name = self.nx_graph.nodes[st_id].get("name_th", st_id) if st_id else "ไม่ระบุ"
            walk = p_data.get("walk_time_min", 0)
            ward = p_data.get("ward", "")
            cat = p_data.get("category", "")
            hours = p_data.get("opening_hours", "")
            fee = p_data.get("admission_fee", "")

            context_parts.append(
                f"[ข้อมูลความสัมพันธ์ของสถานที่จาก Knowledge Graph]:\n"
                f"- สถานที่: {p_name} (เขต: {ward}, หมวดหมู่: {cat})\n"
                f"- สถานีรถไฟที่ใกล้ที่สุด: {st_name} (เดินเท้าประมาณ {walk} นาที)\n"
                f"- เวลาเปิดทำการ: {hours} | ค่าเข้าชม: {fee}"
            )

        # ถ้าพบสถานี 1 แห่ง -> ดึงสถานที่ใกล้เคียงและสถานีข้างเคียง
        elif len(detected_stations) == 1:
            st_id, st_name = detected_stations[0]
            # ตรวจสอบว่าเป็นคำถามถามหาที่เที่ยวรอบๆ หรือถามว่า "จะไปไหนดี"
            is_recommendation = any(k in clean_q for k in ["ไปไหนดี", "ไปที่ไหนดี", "แนะนำ", "เที่ยวไหน", "มีอะไร", "รอบๆ", "ใกล้ๆ", "ที่เที่ยว", "อยู่ที่"])
            if is_recommendation:
                neighbors = self.find_neighboring_attractions(st_id, max_transit_min=15)
                if neighbors:
                    items = []
                    for n in neighbors:
                        items.append(f"- {n['name_th']} ({n['category']}): {n['transit_desc']}")
                    context_parts.append(
                        f"[สถานที่ท่องเที่ยวแนะนำในย่านและสถานีใกล้เคียงจากสถานี {st_name} (Knowledge Graph)]:\n"
                        + "\n".join(items)
                        + f"\n(คำแนะนำสำหรับ AI: ผู้ใช้อยู่ที่ {st_name} ให้แนะนำสถานที่ในย่านนี้และสถานีข้างเคียงที่นั่งรถไฟต่อไปได้ใน 2-10 นาทีตามรายการด้านบนนี้เป็นหลัก ห้ามแนะนำสถานที่ที่อยู่อีกฟากของโตเกียวที่ไกลเกินไป)"
                    )
            else:
                nearby = self.find_nearby_places(st_id)
                if nearby:
                    items = [f"- {n['name_th']} ({n['category']}, เดิน {n['walk_time_min']} นาที ทางออก {n['exit_info']})" for n in nearby]
                    context_parts.append(
                        f"[สถานที่ท่องเที่ยวใกล้สถานี {st_name} จาก Knowledge Graph]:\n"
                        + "\n".join(items)
                    )

        if not context_parts:
            # Fallback ทั่วไป
            return "โครงข่ายความสัมพันธ์: รองรับการเดินทางเชื่อมต่อระหว่างสถานีหลักในโตเกียว (JR Yamanote, Tokyo Metro Ginza, Marunouchi, Hibiya, Asakusa, Oedo, Yurikamome)"

        return "\n\n".join(context_parts)

if __name__ == "__main__":
    pf = TokyoGraphPathfinder()
    print("=" * 60)
    print("TESTING TOKYO GRAPH PATHFINDER")
    print("=" * 60)

    # ทดสอบเส้นทางรถไฟ: Asakusa -> Shibuya
    res = pf.find_shortest_transit("Asakusa", "Shibuya")
    print(f"\n Transit: Asakusa -> Shibuya ({res.get('engine')}):")
    print(f"Total Time: {res.get('total_duration_min')} min | Lines: {res.get('lines_used')}")
    for s in res.get("steps", []):
        print(" ", s)

    # ทดสอบเส้นทางสถานที่: วัดเซ็นโซจิ -> ห้าแยกชิบูย่า
    route = pf.find_place_to_place_route("P_SENSOJI", "P_SHIBUYA_CROSSING")
    print(f"\n Place-to-Place: วัดเซ็นโซจิ -> ห้าแยกชิบูย่า:")
    print(f"Total Time: {route.get('total_duration_min')} min")
    for step in route.get("itinerary", []):
        print(" ", step)
