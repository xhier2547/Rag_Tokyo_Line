"""
src/line_bot/webhook.py
=======================
FastAPI Webhook Server สำหรับรับ Event จาก LINE Messaging API
(Tokyo Smart Transit & Tourism Hybrid Graph RAG)

Flow การทำงาน:
1. รับ HTTP POST Request ที่ /callback จาก LINE Platform
2. ตรวจสอบลายเซ็นความปลอดภัย X-Line-Signature ด้วย WebhookHandler
3. ดึงข้อความคำถามของผู้ใช้ และส่งต่อไปยัง TokyoRAGService
4. สร้างคำตอบพร้อมแท็กอ้างอิง [อ้างอิง: ...] และแนบ Quick Reply สำหรับการถามต่อ
5. ส่งคำตอบกลับไปยังผู้ใช้ผ่าน LINE Reply Message API
"""

import os
import sys
import logging
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    QuickReply,
    QuickReplyButton,
    MessageAction
)

from src.service.rag_service import TokyoRAGService, RAGResponse

load_dotenv()
logger = logging.getLogger("line_bot")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Tokyo Tourism Hybrid Graph RAG - LINE Bot Webhook",
    description="LINE Bot Server เชื่อมต่อ Hybrid RAG และ Knowledge Graph",
    version="1.0.0"
)

# ดึง Credential จาก Environment
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN", "")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET", "")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN) if CHANNEL_ACCESS_TOKEN else None
handler = WebhookHandler(CHANNEL_SECRET) if CHANNEL_SECRET else None

# Lazy load RAG Service เพื่อไม่ให้เสียเวลาก่อนเซิร์ฟเวอร์เปิด
_rag_service: Optional[TokyoRAGService] = None


def get_rag_service() -> TokyoRAGService:
    global _rag_service
    if _rag_service is None:
        logger.info("[LINE Webhook] เริ่มต้นโหลด TokyoRAGService...")
        _rag_service = TokyoRAGService()
    return _rag_service


def build_quick_replies() -> QuickReply:
    """สร้างปุ่ม Quick Reply ให้ผู้ใช้กดถามต่อได้สะดวกรวดเร็ว"""
    items = [
        QuickReplyButton(action=MessageAction(label="🗼 ที่เที่ยวฮิต", text="แนะนำ 5 สถานที่ท่องเที่ยวยอดนิยมใน Tokyo")),
        QuickReplyButton(action=MessageAction(label="⛩️ วัด Senso-ji", text="วัด Sensō-ji มีประวัติและความสำคัญอย่างไร?")),
        QuickReplyButton(action=MessageAction(label="🚆 Shinjuku ไป Shibuya", text="เดินทางจาก Shinjuku ไป Shibuya ใช้สายอะไรและกี่นาที?")),
        QuickReplyButton(action=MessageAction(label="🍣 ตลาดปลา Tsukiji", text="Tsukiji Outer Market มีอะไรน่าสนใจ และไปยังไง?")),
        QuickReplyButton(action=MessageAction(label="🎌 Akihabara Anime", text="Akihabara มีสถานที่อะไรที่เหมาะกับแฟน Anime?")),
        QuickReplyButton(action=MessageAction(label="🗺️ ทริป 1 วัน", text="ช่วยจัดทริป Tokyo 1 วันสำหรับคนมาครั้งแรก"))
    ]
    return QuickReply(items=items)


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Tokyo Smart Transit & Tourism Hybrid Graph RAG LINE Bot",
        "webhook_url": "/callback",
        "health_check": "/health"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "line_token_set": bool(CHANNEL_ACCESS_TOKEN),
        "line_secret_set": bool(CHANNEL_SECRET),
        "gemini_api_key_set": bool(os.getenv("GEMINI_API_KEY"))
    }


@app.post("/callback")
async def callback(request: Request, x_line_signature: Optional[str] = Header(None)):
    """
    Webhook Endpoint สำหรับรับ Event จาก LINE
    """
    if not handler:
        logger.error("CHANNEL_SECRET is not configured in .env")
        raise HTTPException(status_code=500, detail="CHANNEL_SECRET is not configured")

    if not x_line_signature:
        logger.warning("Missing X-Line-Signature Header")
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature")

    body = await request.body()
    body_text = body.decode("utf-8")

    try:
        handler.handle(body_text, x_line_signature)
    except InvalidSignatureError:
        logger.warning("Invalid LINE Webhook Signature")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"Error handling webhook event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content={"status": "OK"})


if handler:
    @handler.add(MessageEvent, message=TextMessage)
    def handle_text_message(event: MessageEvent):
        """
        ประมวลผลข้อความตัวอักษรที่ส่งมาจากผู้ใช้ใน LINE
        """
        user_query = event.message.text.strip()
        logger.info(f"[LINE Message Received] '{user_query}' from User: {event.source.user_id}")

        try:
            # 1. ส่งคำถามเข้าสู่ Hybrid RAG Service
            service = get_rag_service()
            response: RAGResponse = service.answer_query(
                query=user_query,
                mode="gemini"
            )

            # 2. จัดรูปแบบข้อความตอบกลับ
            formatted_reply = f"{response.answer}\n\n"
            if response.citations:
                cits_str = "\n".join([f"• {c}" for c in response.citations[:4]])
                formatted_reply += f"📚 แหล่งอ้างอิงยืนยัน:\n{cits_str}\n\n"

            formatted_reply += f"⏱️ ประมวลผล: {response.latency_sec:.2f}s | โมเดล: {response.model_name}"

            # 3. เตรียม Quick Reply ปุ่มลัด
            quick_reply = build_quick_replies()

            # 4. ส่งข้อความตอบกลับไปยัง LINE
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=formatted_reply, quick_reply=quick_reply)
            )
            logger.info(f"[LINE Reply Sent] Successfully replied to {event.source.user_id}")

        except Exception as e:
            logger.error(f"[LINE Error] Failed to process message: {e}")
            error_message = (
                f"ขออภัยครับ เกิดข้อผิดพลาดในการค้นหาข้อมูล: {str(e)}\n\n"
                "กรุณาลองพิมพ์ถามใหม่อีกครั้ง เช่น 'เดินทางจาก Shinjuku ไป Shibuya ใช้สายอะไร'"
            )
            try:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=error_message, quick_reply=build_quick_replies())
                )
            except Exception:
                pass
