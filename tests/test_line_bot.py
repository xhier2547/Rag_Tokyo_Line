"""
tests/test_line_bot.py
======================
Automated Unit Tests สำหรับโมดูล LINE Bot Integration
- ทดสอบการสร้างรูปภาพ Rich Menu ขนาด 2500x1686
- ทดสอบโครงสร้าง RichMenu Object และ 6 Areas
- ทดสอบ FastAPI Endpoints (/ และ /health)
- ทดสอบความปลอดภัยของ Webhook Signature (/callback)
- ทดสอบการสร้าง Quick Reply Buttons
"""

import os
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from src.line_bot.rich_menu_creator import generate_rich_menu_image, create_rich_menu_object
from src.line_bot.webhook import app, build_quick_replies


@pytest.fixture
def client():
    return TestClient(app)


def test_rich_menu_image_generation(tmp_path):
    """ทดสอบการสร้างรูปภาพ Rich Menu ขนาดมาตรฐาน 2500 x 1686 พิกเซล"""
    test_img_path = str(tmp_path / "test_rich_menu.png")
    out_path = generate_rich_menu_image(output_path=test_img_path)

    assert os.path.exists(out_path)
    with Image.open(out_path) as im:
        assert im.size == (2500, 1686)
        assert im.format == "PNG"


def test_rich_menu_object_structure():
    """ทดสอบโครงสร้างข้อมูล RichMenu สำหรับ LINE API"""
    rm = create_rich_menu_object()
    assert rm.size.width == 2500
    assert rm.size.height == 1686
    assert len(rm.areas) == 6  # ต้องมี 6 ปุ่มครบ
    assert rm.selected is True
    assert "เมนู" in rm.chat_bar_text


def test_quick_replies_generation():
    """ทดสอบการสร้างปุ่ม Quick Reply สำหรับแชต"""
    qr = build_quick_replies()
    assert len(qr.items) == 6
    labels = [btn.action.label for btn in qr.items]
    assert any("ที่เที่ยว" in l for l in labels)
    assert any("Shinjuku" in l for l in labels)
    assert any("วัด" in l for l in labels)


def test_api_root_and_health(client):
    """ทดสอบ Health check endpoint ของ Webhook Server"""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["status"] == "online"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    data = res_health.json()
    assert data["status"] == "healthy"
    assert "line_token_set" in data


def test_webhook_signature_rejection(client):
    """ทดสอบว่า Request ที่ไม่มี Signature ถูกปฏิเสธ (400 Bad Request) เพื่อความปลอดภัย"""
    res = client.post("/callback", json={"events": []})
    assert res.status_code == 400


def test_webhook_valid_signature_dispatch(client, monkeypatch):
    """ทดสอบว่า Request ที่มี Signature ถูกต้อง ได้รับ 200 OK ทันที (Background Task)"""
    import base64
    import hashlib
    import hmac
    from src.line_bot.webhook import CHANNEL_SECRET

    body = b'{"destination":"Uxxx","events":[]}'
    hash_obj = hmac.new(CHANNEL_SECRET.encode('utf-8'), body, hashlib.sha256).digest()
    valid_signature = base64.b64encode(hash_obj).decode('utf-8')

    headers = {"X-Line-Signature": valid_signature}
    res = client.post("/callback", content=body, headers=headers)
    assert res.status_code == 200
    assert res.json() == {"status": "OK"}

