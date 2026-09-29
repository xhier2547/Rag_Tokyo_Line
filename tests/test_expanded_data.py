"""
tests/test_expanded_data.py
===========================
Automated Integration Tests สำหรับชุดข้อมูลที่ขยายใหม่:
1. ตรวจสอบจำนวนข้อมูลใน Dataset (Places=20, Stations=20, Lines=11, Hotels=10)
2. ตรวจสอบการค้นหา Hybrid Context สำหรับสถานที่ใหม่ (Imperial Palace, teamLab, Ameyoko, Takeshita, Toyosu)
3. ตรวจสอบการค้นหาโรงแรมและที่พัก (Hotels & Accommodations Retrieval)
4. ตรวจสอบการคำนวณเส้นทาง Graph Pathfinder กับสถานีและสายรถไฟใหม่
"""

import os
import unittest
import pandas as pd

from src.data_pipeline.processor import PROCESSED_DIR
from src.hybrid.engine import TokyoHybridRAGEngine
from src.graph.pathfinder import TokyoGraphPathfinder


class TestExpandedData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hybrid_engine = TokyoHybridRAGEngine()
        cls.pathfinder = TokyoGraphPathfinder()

    def test_01_dataset_files_and_counts(self):
        """ตรวจสอบว่าไฟล์ CSV ทั้งหมดถูกสร้างอย่างถูกต้องและมีจำนวนครบตามที่ขยาย"""
        places_df = pd.read_csv(os.path.join(PROCESSED_DIR, "places.csv"))
        stations_df = pd.read_csv(os.path.join(PROCESSED_DIR, "stations.csv"))
        lines_df = pd.read_csv(os.path.join(PROCESSED_DIR, "lines.csv"))
        hotels_df = pd.read_csv(os.path.join(PROCESSED_DIR, "hotels.csv"))
        transit_df = pd.read_csv(os.path.join(PROCESSED_DIR, "transit_edges.csv"))
        ps_df = pd.read_csv(os.path.join(PROCESSED_DIR, "place_station_edges.csv"))

        self.assertEqual(len(places_df), 20, "Places count should be exactly 20")
        self.assertEqual(len(stations_df), 20, "Stations count should be exactly 20")
        self.assertEqual(len(lines_df), 11, "Lines count should be exactly 11")
        self.assertEqual(len(hotels_df), 10, "Hotels count should be exactly 10")
        self.assertGreaterEqual(len(transit_df), 60, "Transit edges should be at least 60")
        self.assertEqual(len(ps_df), 20, "Place-station edges should be exactly 20")

    def test_02_new_places_retrieval(self):
        """ทดสอบการค้นหา Hybrid Context กับสถานที่ท่องเที่ยวใหม่ 5 แห่ง"""
        queries = [
            ("ประวัติและเวลาเปิดของพระราชวังอิมพีเรียล", "พระราชวังอิมพีเรียล"),
            ("teamLab Planets นิทรรศการศิลปะดิจิทัล มีอะไรเด่น", "teamLab"),
            ("ของกินสตรีทฟู้ด ตลาดอะเมโยโกะ มีอะไรบ้าง", "อะเมโยโกะ"),
            ("ร้านเครปและแฟชั่นวัยรุ่น ถนนทาเคชิตะ ฮาราจูกุ", "ทาเคชิตะ"),
            ("ตลาดปลาโทโยสุ เซ็นเคียคุบันไร มีไฮไลต์อะไรบ้าง", "โทโยสุ")
        ]
        for query, expected_text in queries:
            result = self.hybrid_engine.retrieve_hybrid_context(query=query)
            self.assertGreater(result.vector_docs_count, 0, f"Search should return chunks for '{query}'")
            self.assertTrue(
                expected_text.lower() in result.final_context.lower(),
                f"Expected '{expected_text}' in final_context for query '{query}'"
            )

    def test_03_hotel_retrieval(self):
        """ทดสอบการค้นหาโรงแรมและที่พัก (Hotels & Accommodations)"""
        queries = [
            ("แนะนำโรงแรมใกล้สถานีชินจูกุ", ["โรงแรม", "ชินจูกุ"]),
            ("โรงแรมวิวโตเกียวสกายทรี แถวอาซากุสะ", ["อาซากุสะ", "โรงแรม"]),
            ("โรงแรมที่มีบ่อออนเซ็น แถวอากิฮาบาระ", ["อากิฮาบาระ", "โรงแรม"])
        ]
        for query, expected_keywords in queries:
            result = self.hybrid_engine.retrieve_hybrid_context(query=query)
            self.assertGreater(result.vector_docs_count, 0, f"Should return chunks for '{query}'")
            matched = all(k.lower() in result.final_context.lower() for k in expected_keywords)
            self.assertTrue(matched, f"Expected keywords {expected_keywords} in context for query '{query}'")

    def test_04_graph_pathfinder_with_new_stations(self):
        """ทดสอบการค้นหาเส้นทางรถไฟด้วย NetworkX/Neo4j กับสถานีใหม่"""
        # 1. Tokyo -> Korakuen (Marunouchi Line)
        path1 = self.pathfinder.find_shortest_transit("สถานีโตเกียว", "สถานีโคระคุเอ็น")
        self.assertTrue(path1["success"], "Should find route between Tokyo and Korakuen")
        self.assertEqual(path1["total_duration_min"], 9)

        # 2. Shibuya -> Omotesando (Ginza Line)
        path2 = self.pathfinder.find_shortest_transit("สถานีชิบูย่า", "สถานีโอโมเตะซันโด")
        self.assertTrue(path2["success"], "Should find route between Shibuya and Omotesando")
        self.assertEqual(path2["total_duration_min"], 2)

        # 3. Shimbashi -> Shijo-mae (Yurikamome Line to Toyosu Market)
        path3 = self.pathfinder.find_shortest_transit("สถานีชิมบาชิ", "สถานีชิโจมาเอะ")
        self.assertTrue(path3["success"], "Should find route between Shimbashi and Shijo-mae")
        self.assertEqual(path3["total_duration_min"], 22)


if __name__ == "__main__":
    unittest.main()
