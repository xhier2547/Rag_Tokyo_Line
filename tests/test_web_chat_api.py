"""
tests/test_web_chat_api.py
===========================
Automated Integration Tests สำหรับ Web Chat API (FastAPI + React Endpoint)
1. ทดสอบการเข้าถึงหน้าเว็บ / และ /demo
2. ทดสอบ API POST /api/chat
3. ทดสอบ Multi-turn Conversation ผ่าน Session ID
4. ทดสอบ Reset Session
"""

import unittest
from fastapi.testclient import TestClient
from src.line_bot.webhook import app


class TestWebChatAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_serve_html_demo(self):
        """ทดสอบการเสิร์ฟหน้าเว็บแอปพลิเคชัน /demo และ /"""
        res = self.client.get("/demo")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.headers["content-type"])
        self.assertIn("Tokyo RAG", res.text)
        self.assertIn("React", res.text)

    def test_02_post_chat_api(self):
        """ทดสอบ API ตอบคำถามผ่าน /api/chat"""
        payload = {
            "message": "วัดเซ็นโซจิมีอะไรน่าสนใจบ้าง",
            "session_id": "test_web_user_1"
        }
        res = self.client.post("/api/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("answer", data)
        self.assertIn("intent", data)
        self.assertIn("cards", data)
        self.assertIsInstance(data["cards"], list)

    def test_03_web_multiturn_flow(self):
        """ทดสอบคำถามต่อเนื่อง (Multi-turn) ผ่าน Web API"""
        session_id = "test_web_multiturn"

        # Turn 1
        self.client.post("/api/chat", json={
            "message": "วัดเซ็นโซจิ",
            "session_id": session_id
        })

        # Turn 2: ถามจากอิเคะโบะคุโระ
        res2 = self.client.post("/api/chat", json={
            "message": "ฉันอยู่ที่อิเคะโบะคุโระ ต้องการไปที่นี่ ต้องไปอย่างไร",
            "session_id": session_id
        })
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertIn("อิเคะบุคุโระ", data2["resolved_query"])

        # Reset session
        reset_res = self.client.post("/api/chat/reset", json={"session_id": session_id})
        self.assertEqual(reset_res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
