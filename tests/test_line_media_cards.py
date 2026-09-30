"""
tests/test_line_media_cards.py
==============================
Automated Tests สำหรับระบบแสดงรูปภาพสถานที่และการ์ดแบบ Interactive บน LINE Bot:
1. ตรวจสอบความถูกต้องของ Media Catalog (URLs, ชื่อสถานที่, หมวดหมู่)
2. ตรวจสอบการตรวจจับ Entity จากข้อความ (Entity Detection)
3. ตรวจสอบโครงสร้าง LINE Flex Message (Bubble & Carousel)
4. ตรวจสอบความยาวปุ่ม Quick Reply ไม่เกิน 20 ตัวอักษรตามข้อกำหนดของ LINE
"""

import unittest
from src.line_bot.media_catalog import (
    PLACE_MEDIA_CATALOG,
    HOTEL_MEDIA_CATALOG,
    find_matched_entities
)
from src.line_bot.flex_cards import (
    create_entity_bubble,
    build_flex_message_from_entities,
    build_contextual_quick_replies
)
from linebot.models import FlexSendMessage, QuickReply


class TestLineMediaCards(unittest.TestCase):
    def test_01_media_catalog_integrity(self):
        """ตรวจสอบว่าแคตตาล็อกมีข้อมูลครบถ้วนและ Image URL เป็น HTTPS"""
        self.assertGreaterEqual(len(PLACE_MEDIA_CATALOG), 20, "Should have at least 20 places in catalog")
        self.assertGreaterEqual(len(HOTEL_MEDIA_CATALOG), 5, "Should have at least 5 hotels in catalog")

        for pid, data in PLACE_MEDIA_CATALOG.items():
            self.assertTrue(data["image_url"].startswith("https://"), f"{pid} image must be HTTPS")
            self.assertTrue(len(data["name_th"]) > 0, f"{pid} must have Thai name")
            self.assertTrue(len(data["nearest_station"]) > 0, f"{pid} must have nearest station")
            self.assertTrue(len(data["keywords"]) > 0, f"{pid} must have keywords for matching")

        for hid, data in HOTEL_MEDIA_CATALOG.items():
            self.assertTrue(data["image_url"].startswith("https://"), f"{hid} image must be HTTPS")
            self.assertTrue(len(data["name_th"]) > 0, f"{hid} must have Thai name")
            self.assertTrue("price_range" in data, f"{hid} must have price_range")

        takeshita_image = PLACE_MEDIA_CATALOG["P_TAKESHITA_STREET"]["image_url"]
        self.assertIn("Takeshita_Street_in_Harajuku", takeshita_image)

    def test_02_matched_entities_detection(self):
        """ทดสอบฟังก์ชันตรวจจับสถานที่และโรงแรมจากข้อความคำตอบและ Citations"""
        # เคส 1: วัดเซ็นโซจิ
        res1 = find_matched_entities(text="วัดเซ็นโซจิ หรือวัดอาซากุสะ มีโคมแดงยักษ์อันเลื่องชื่อ")
        self.assertGreater(len(res1), 0)
        self.assertEqual(res1[0]["id"], "P_SENSOJI")

        # เคส 2: โรงแรมก็อดซิลล่า ชินจูกุ
        res2 = find_matched_entities(text="แนะนำโรงแรมเกรเซอรี ชินจูกุ มีหัวก็อดซิลล่า")
        self.assertGreater(len(res2), 0)
        self.assertEqual(res2[0]["id"], "H_GRACERY_SHINJUKU")

        # เคส 3: ตรวจจับหลายสถานที่ (เช่น แนะนำ 3 ที่)
        res3 = find_matched_entities(
            text="ขอแนะนำห้าแยกชิบูย่า และไปต่อที่โตเกียวทาวเวอร์",
            citations=["ห้าแยกชิบูย่า", "โตเกียวทาวเวอร์"]
        )
        self.assertGreaterEqual(len(res3), 2)
        ids = [e["id"] for e in res3]
        self.assertIn("P_SHIBUYA_CROSSING", ids)
        self.assertIn("P_TOKYO_TOWER", ids)

    def test_03_flex_message_bubble_and_carousel(self):
        """ทดสอบการสร้าง Flex Message Bubble เดี่ยว และ Carousel หลายสถานที่"""
        entity = PLACE_MEDIA_CATALOG["P_SENSOJI"]
        bubble = create_entity_bubble(entity)

        # ตรวจสอบโครงสร้าง Hero
        self.assertEqual(bubble["type"], "bubble")
        self.assertEqual(bubble["hero"]["type"], "image")
        self.assertEqual(bubble["hero"]["aspectRatio"], "20:13")
        self.assertEqual(bubble["hero"]["url"], entity["image_url"])

        # ตรวจสอบปุ่ม Footer Action
        buttons = bubble["footer"]["contents"]
        self.assertEqual(len(buttons), 2)
        self.assertEqual(buttons[0]["action"]["type"], "message")
        self.assertTrue(buttons[0]["action"]["label"].startswith("🚆"))

        # ทดสอบ Wrap เป็น FlexSendMessage เดี่ยว
        flex_single = build_flex_message_from_entities([entity])
        self.assertIsInstance(flex_single, FlexSendMessage)
        self.assertEqual(flex_single.contents.type, "bubble")

        # ทดสอบ Wrap เป็น FlexSendMessage แบบ Carousel
        entities_multi = [PLACE_MEDIA_CATALOG["P_SENSOJI"], PLACE_MEDIA_CATALOG["P_TOKYO_SKYTREE"]]
        flex_multi = build_flex_message_from_entities(entities_multi)
        self.assertIsInstance(flex_multi, FlexSendMessage)
        self.assertEqual(flex_multi.contents.type, "carousel")
        self.assertEqual(len(flex_multi.contents.contents), 2)

    def test_04_contextual_quick_replies(self):
        """ตรวจสอบความยาว label ของปุ่ม Quick Reply ต้องไม่เกิน 20 ตัวอักษรตามข้อกำหนด LINE"""
        entities = [PLACE_MEDIA_CATALOG["P_SENSOJI"]]
        qr = build_contextual_quick_replies(entities)
        self.assertIsInstance(qr, QuickReply)
        self.assertGreater(len(qr.items), 0)

        for item in qr.items:
            label = item.action.label
            self.assertLessEqual(len(label), 20, f"Quick Reply label '{label}' exceeds 20 chars limit!")

        # ทดสอบ Fallback Quick Reply
        qr_fallback = build_contextual_quick_replies([])
        self.assertGreater(len(qr_fallback.items), 0)
        for item in qr_fallback.items:
            self.assertLessEqual(len(item.action.label), 20)

    def test_05_origin_exclusion_for_location_queries(self):
        """ทดสอบการคัดกรองสถานที่ต้นทางออกเมื่อผู้ใช้ถามว่า 'อยู่ที่... จะไปไหนดี' เพื่อแนะนำสถานที่ปลายทางเป็นหลัก"""
        query = "แล้วถ้าผมอยู่ที่ชิบูย่าละ จะไปที่ไหนดี"
        answer = "แนะนำไปเที่ยวถนนทาเคชิตะ ย่านฮาราจูกุ หรือศาลเจ้าเมจิ จากห้าแยกชิบูย่า"
        matched = find_matched_entities(text=answer, query=query)

        self.assertGreater(len(matched), 0)
        # ตรวจสอบว่าสถานที่แรกที่แนะนำไม่ใช่ห้าแยกชิบูย่า (ตำแหน่งที่ผู้ใช้อยู่แล้ว)
        self.assertNotEqual(matched[0]["id"], "P_SHIBUYA_CROSSING", "Top recommendation card should be a destination, not the user's current origin")
        # ตรวจสอบว่าฮาราจูกุหรือศาลเจ้าเมจิถูกนำมาแสดง
        matched_ids = [m["id"] for m in matched]
        self.assertIn("P_TAKESHITA_STREET", matched_ids)
        self.assertIn("P_MEIJI_JINGU", matched_ids)

    def test_06_message_order_text_first_card_second(self):
        """ทดสอบโครงสร้างชุดข้อความที่จะส่ง ให้ข้อความคำอธิบายอยู่ก่อน และการ์ด Flex Message อยู่ด้านล่าง"""
        from linebot.models import TextSendMessage

        entity = PLACE_MEDIA_CATALOG["P_SENSOJI"]
        flex_card = build_flex_message_from_entities([entity])
        quick_reply = build_contextual_quick_replies([entity])

        # จำลองการจัดลำดับข้อความใน webhook.py
        messages_to_send = []
        formatted_reply = "รายละเอียดการเดินทาง..."

        if flex_card:
            messages_to_send.append(TextSendMessage(text=formatted_reply))
            flex_card.quick_reply = quick_reply
            messages_to_send.append(flex_card)
        else:
            messages_to_send.append(TextSendMessage(text=formatted_reply, quick_reply=quick_reply))

        # ตรวจสอบว่าข้อความแรกเป็น Text และข้อความที่สองเป็น Flex
        self.assertEqual(len(messages_to_send), 2)
        self.assertIsInstance(messages_to_send[0], TextSendMessage)
        self.assertIsInstance(messages_to_send[1], FlexSendMessage)
        # ตรวจสอบว่า Quick Reply ถูกแนบไว้ที่การ์ด Flex ด้านล่างสุด
        self.assertIsNone(messages_to_send[0].quick_reply)
        self.assertIsNotNone(messages_to_send[1].quick_reply)


if __name__ == "__main__":
    unittest.main()

