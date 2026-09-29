"""
tests/test_line_multiturn.py
============================
Automated Tests สำหรับระบบ Multi-turn Conversation Session & Contextual Query Resolution:
1. ทดสอบการบันทึกและสกัดข้อมูลบริบท (Session State & Entity Tracking)
2. ทดสอบการแปลงคำถามต่อเนื่อง (Follow-up Query Resolution):
   Turn 1: "แนะนำโรงแรมใกล้สถานี Shibuya"
   Turn 2: "แล้วถ้าฉันอยู่ที่กินซ่า ต้องไปอย่างไร"
   -> ขยายเป็นคำถามการเดินทางจาก Ginza ไปยังโรงแรมใกล้สถานี Shibuya
3. ทดสอบ Graph RAG Pathfinding สำหรับคำถามเดินทางระหว่างสถานีและโรงแรม
4. ทดสอบการเลือกการ์ดรูปภาพโรงแรมเป้าหมายปลายทาง (Destination Priority)
"""

import unittest
from src.line_bot.session_manager import SessionManager
from src.graph.pathfinder import TokyoGraphPathfinder
from src.line_bot.media_catalog import find_matched_entities


class TestLineMultiTurn(unittest.TestCase):
    def setUp(self):
        self.session_mgr = SessionManager(session_ttl_sec=600)
        self.pathfinder = TokyoGraphPathfinder()

    def test_01_session_state_and_resolution(self):
        """ทดสอบการจำลองบทสนทนา 2 รอบ และขยายบริบทคำถามให้สมบูรณ์"""
        user_id = "test_user_multiturn_1"

        # Turn 1: ผู้ใช้ถามหาโรงแรมใกล้สถานี Shibuya
        turn1_query = "แนะนำโรงแรมใกล้สถานี Shibuya"
        turn1_answer = "ขอแนะนำ โรงแรม ชิบูย่า สตรีม เอ็กเซล โฮเทล โทคิว (Shibuya Stream Excel Hotel Tokyu) ตั้งอยู่ใกล้สถานี Shibuya เดินประมาณ 2 นาที"
        matched_t1 = [
            {
                "id": "H_SHIBUYA_STREAM_EXCEL",
                "name_th": "ชิบูย่า สตรีม เอ็กเซล โฮเทล โทคิว",
                "nearest_station": "สถานี Shibuya"
            }
        ]

        self.session_mgr.update_session(
            user_id=user_id,
            query=turn1_query,
            resolved_query=turn1_query,
            answer=turn1_answer,
            matched_entities=matched_t1
        )

        sess = self.session_mgr.get_or_create_session(user_id)
        self.assertEqual(sess.last_target_station, "Shibuya")
        self.assertEqual(sess.last_target_place, "ชิบูย่า สตรีม เอ็กเซล โฮเทล โทคิว")

        # Turn 2: ผู้ใช้ถามต่อ "แล้วถ้าฉันอยู่ที่กินซ่า ต้องไปอย่างไร"
        turn2_query = "แล้วถ้าฉันอยู่ที่กินซ่า ต้องไปอย่างไร"
        resolved_q, hint = self.session_mgr.resolve_contextual_query(user_id, turn2_query)

        # ตรวจสอบว่า resolved query มีทั้งต้นทาง (กินซ่า) และปลายทาง (ชิบูย่า สตรีม / Shibuya)
        self.assertIn("กินซ่า", resolved_q)
        self.assertIn("ชิบูย่า สตรีม", resolved_q)
        self.assertIn("Shibuya", resolved_q)
        self.assertIsNotNone(hint)

    def test_02_graph_transit_from_ginza_to_shibuya_hotel(self):
        """ทดสอบว่า Knowledge Graph สามารถคำนวณเส้นทางจากสถานีกินซ่าไปยังสถานีชิบูย่าได้อย่างถูกต้อง"""
        resolved_query = "เดินทางจาก สถานีกินซ่า (Ginza) ไปยัง โรงแรม ชิบูย่า สตรีม เอ็กเซล โฮเทล โทคิว สถานี Shibuya ต้องไปอย่างไรและใช้สายรถไฟอะไร"
        graph_context = self.pathfinder.extract_graph_context_for_rag(resolved_query)

        # ต้องพบข้อมูลเส้นทางรถไฟ
        self.assertIn("[ข้อมูลเส้นทางรถไฟจาก Knowledge Graph]", graph_context)
        self.assertIn("สถานีกินซ่า", graph_context)
        self.assertIn("สถานีชิบูย่า", graph_context)
        # ตรวจสอบสายรถไฟ (Tokyo Metro Ginza Line หรือ Hanzomon Line)
        self.assertTrue(
            "Ginza Line" in graph_context or "สายรถไฟ" in graph_context,
            "Graph context should provide transit line information"
        )

    def test_03_media_catalog_selects_destination_hotel_card(self):
        """ทดสอบว่าการ์ดรูปภาพที่แสดงเป็นการ์ดโรงแรมปลายทาง (Shibuya Stream) ไม่ใช่ย่านต้นทาง (Ginza)"""
        resolved_query = "เดินทางจาก สถานีกินซ่า (Ginza) ไปยัง โรงแรม ชิบูย่า สตรีม เอ็กเซล โฮเทล โทคิว สถานี Shibuya"
        answer = "สำหรับการเดินทางจากสถานีกินซ่า ไปยังโรงแรม ชิบูย่า สตรีม เอ็กเซล โฮเทล โทคิว ให้ขึ้นรถไฟสาย Ginza Line ไปลงสถานี Shibuya..."

        matched = find_matched_entities(text=answer, query=resolved_query)

        self.assertGreater(len(matched), 0)
        # การ์ดอันดับแรกต้องเป็นโรงแรมชิบูย่า สตรีม
        self.assertEqual(matched[0]["id"], "H_SHIBUYA_STREAM_EXCEL")
        # ต้องไม่มีการ์ด Ginza ซึ่งเป็นต้นทาง
        matched_ids = [m["id"] for m in matched]
        self.assertNotIn("P_GINZA_SIX", matched_ids)


if __name__ == "__main__":
    unittest.main()
