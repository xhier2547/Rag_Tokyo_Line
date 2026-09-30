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
import re
import logging
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi import FastAPI, Request, Header, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse

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
from src.line_bot.media_catalog import find_matched_entities
from src.line_bot.flex_cards import build_flex_message_from_entities, build_contextual_quick_replies
from src.line_bot.session_manager import get_session_manager

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
    """สร้างปุ่ม Quick Reply ให้ผู้ใช้กดถามต่อได้สะดวกรวดเร็ว (จำกัดความยาว label <= 20 ตัวอักษรตามข้อกำหนดของ LINE)"""
    raw_buttons = [
        ("🗼 ที่เที่ยวฮิต", "แนะนำ 5 สถานที่ท่องเที่ยวยอดนิยมใน Tokyo"),
        ("⛩️ วัด Senso-ji", "วัด Sensō-ji มีประวัติและความสำคัญอย่างไร?"),
        ("🚆 รถไฟ Shinjuku", "เดินทางจาก Shinjuku ไป Shibuya ใช้สายอะไรและกี่นาที?"),
        ("🍣 ตลาดปลา Tsukiji", "Tsukiji Outer Market มีอะไรน่าสนใจ และไปยังไง?"),
        ("🎌 Akihabara Anime", "Akihabara มีสถานที่อะไรที่เหมาะกับแฟน Anime?"),
        ("🗺️ ทริป 1 วัน", "ช่วยจัดทริป Tokyo 1 วันสำหรับคนมาครั้งแรก")
    ]
    items = [
        QuickReplyButton(action=MessageAction(label=label[:20], text=text))
        for label, text in raw_buttons
    ]
    return QuickReply(items=items)



@app.on_event("startup")
def startup_event():

    """โหลด RAG Service ล่วงหน้า (Pre-warm) เพื่อให้พร้อมตอบคำถามทันทีตั้งแต่ข้อแรก"""
    logger.info("[LINE Webhook Startup] กำลังเตรียมความพร้อม RAG Engine & Model Cache...")
    get_rag_service()
    logger.info("[LINE Webhook Startup] ระบบพร้อมให้บริการตอบคำถามเรียบร้อย!")


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
async def callback(
    request: Request,
    background_tasks: BackgroundTasks,
    x_line_signature: Optional[str] = Header(None)
):
    """
    Webhook Endpoint สำหรับรับ Event จาก LINE
    - ตรวจสอบความถูกต้องของ Signature ทันที
    - ส่งมอบงานให้ BackgroundTasks ประมวลผล RAG
    - ส่ง HTTP 200 OK กลับไปยัง LINE ทันทีใน < 50ms เพื่อป้องกัน LINE Timeout
    """
    if not handler:
        logger.error("CHANNEL_SECRET is not configured in .env")
        raise HTTPException(status_code=500, detail="CHANNEL_SECRET is not configured")

    if not x_line_signature:
        logger.warning("Missing X-Line-Signature Header")
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature")

    body = await request.body()
    body_text = body.decode("utf-8")

    # ตรวจสอบลายเซ็นก่อนส่งต่อ
    try:
        is_valid = handler.parser.signature_validator.validate(body_text, x_line_signature)
        if not is_valid:
            logger.warning("Invalid LINE Webhook Signature")
            raise HTTPException(status_code=400, detail="Invalid signature")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signature validation error: {e}")
        raise HTTPException(status_code=400, detail="Signature error")

    # ส่งต่อให้ BackgroundTasks รันการดึงข้อมูลและตอบกลับ
    background_tasks.add_task(handler.handle, body_text, x_line_signature)

    return JSONResponse(content={"status": "OK"})



def format_line_reply(response: RAGResponse) -> str:
    """
    จัดรูปแบบข้อความตอบกลับของ LINE Bot ให้สวยงาม อ่านง่าย มีระดับแบบ Professional Concierge
    - แปลง LaTeX arrow ($\rightarrow$) เป็น unicode arrow ➔
    - แปลงรหัสสถานี ST_... เป็นชื่อสถานีภาษาไทย/อังกฤษที่เข้าใจง่าย
    - ทำความสะอาด bullet points ให้เป็นระเบียบ สวยงาม สบายตา
    - กรองรายการอ้างอิงไม่ให้แสดงซ้ำซ้อน (Deduplication)
    - เพิ่มเส้นคั่นดีไซน์ ────────────────────── และไอคอนกำกับ
    """
    text = response.answer.strip()

    # 1. แปลงสัญลักษณ์ลูกศรและรหัสทางคณิตศาสตร์
    text = text.replace(r"$\rightarrow$", "➔").replace(r"\rightarrow", "➔").replace(r"->", "➔")

    # 2. แปลงรหัสสถานีภายในเป็นชื่อสถานีที่อ่านง่าย
    station_map = {
        "ST_SHIBUYA": "สถานี Shibuya",
        "ST_SHINJUKU": "สถานี Shinjuku",
        "ST_TOKYO": "สถานี Tokyo",
        "ST_ASAKUSA": "สถานี Asakusa",
        "ST_GINZA": "สถานี Ginza",
        "ST_UENO": "สถานี Ueno",
        "ST_HARAJUKU": "สถานี Harajuku",
        "ST_AKIHABARA": "สถานี Akihabara",
        "ST_ROPPONGI": "สถานี Roppongi",
        "ST_OSHIAGE": "สถานี Oshiage (Skytree)",
        "ST_TSUKIJI": "สถานี Tsukiji",
        "ST_DAIBA": "สถานี Daiba (Odaiba)",
    }
    for st_id, st_name in station_map.items():
        text = text.replace(st_id, st_name)

    # 3. จัดการกรณีข้อความ Fallback ที่มีแท็กระบบดิบ
    if "=== ข้อมูลความสัมพันธ์และเส้นทาง" in text:
        text = text.replace("=== ข้อมูลความสัมพันธ์และเส้นทาง (Knowledge Graph) ===", "🚆 แผนการเดินทาง (Knowledge Graph):")
        text = text.replace("[ข้อมูลเส้นทางรถไฟจาก Knowledge Graph]:", "")
        text = re.sub(r"=== ข้อมูลรายละเอียดสถานที่.*?===", "\n📍 ข้อมูลสถานที่เพิ่มเติม:", text)
        text = re.sub(r"แหล่งอ้างอิงยืนยัน:.*", "", text, flags=re.DOTALL)

    # 4. ปรับปรุง Bullet points และความเรียบร้อย
    # ลบดอกจัน ** ทั้งหมด (LINE ไม่เรนเดอร์ Markdown bold)
    text = text.replace("**", "")

    # ลบแท็ก [อ้างอิง: ...] ที่เกะกะกลางบรรทัดออก เพื่อให้อ่านง่าย สบายตา
    text = re.sub(r"\s*-\s*\[อ้างอิง:[^\]]+\]", "", text)
    text = re.sub(r"\[อ้างอิง:[^\]]+\]", "", text)

    # แปลง sub-bullet * เป็น -
    text = re.sub(r"^\s{2,}\*\s+", "   - ", text, flags=re.MULTILINE)

    # 5. สกัดและกรองรายการอ้างอิงไม่ให้ซ้ำซ้อน
    unique_cits = []
    for c in response.citations:
        cleaned_c = re.sub(r"\s*-\s*(ส่วนที่\s*\d+|ข้อมูลการเดินทาง.*)", "", c).strip()
        cleaned_c = re.sub(r"\(.*?\)", "", cleaned_c).strip()
        for st_id, st_name in station_map.items():
            cleaned_c = cleaned_c.replace(st_id, st_name)
        if cleaned_c and cleaned_c not in unique_cits and len(cleaned_c) > 2:
            unique_cits.append(cleaned_c)

    # 6. ประกอบข้อความตอบกลับ
    parts = [text.strip(), ""]
    if unique_cits:
        cits_str = "\n".join([f"• {c}" for c in unique_cits[:4]])
        parts.append(f"──────────────────────\n📚 ข้อมูลอ้างอิงยืนยัน:\n{cits_str}\n")
    else:
        parts.append("──────────────────────\n")

    model_display = "Gemini 3.1 Flash Lite" if "gemini" in response.model_name.lower() else response.model_name
    parts.append(f"⚡ เวลาประมวลผล: {response.latency_sec:.2f}s | โมเดล: {model_display}")

    return "\n".join(parts)


if handler:
    @handler.add(MessageEvent, message=TextMessage)
    def handle_text_message(event: MessageEvent):
        """
        ประมวลผลข้อความตัวอักษรที่ส่งมาจากผู้ใช้ใน LINE
        - ส่ง Flex Message การ์ดรูปภาพสถานที่/โรงแรม พร้อมปุ่ม Interactive Actions
        - ส่ง Text Message คำอธิบายเชิงลึกจาก Hybrid RAG
        - แนบ Contextual Quick Reply ให้แตะถามต่อได้ทันที
        """
        user_id = event.source.user_id
        user_query = event.message.text.strip()
        logger.info(f"[LINE Message Received] '{user_query}' from User: {user_id}")

        try:
            # 1. จัดการบริบทการสนทนาต่อเนื่อง (Multi-turn Context Resolution)
            session_mgr = get_session_manager()
            resolved_query, context_hint = session_mgr.resolve_contextual_query(
                user_id=user_id,
                current_query=user_query
            )

            # 2. ส่งคำถามที่สมบูรณ์เข้าสู่ Hybrid RAG Service
            service = get_rag_service()
            response: RAGResponse = service.answer_query(
                query=resolved_query,
                mode="gemini"
            )

            # 3. จัดรูปแบบข้อความตอบกลับให้สวยงาม ระดับมืออาชีพ
            formatted_reply = format_line_reply(response)

            # 4. ค้นหาสถานที่หรือโรงแรมที่เกี่ยวข้องเพื่อสร้างการ์ดรูปภาพ (Flex Card)
            matched_entities = find_matched_entities(
                text=response.answer,
                citations=response.citations,
                query=resolved_query
            )

            # 5. บันทึกประวัติและบริบทการสนทนาลง Session
            session_mgr.update_session(
                user_id=user_id,
                query=user_query,
                resolved_query=resolved_query,
                answer=response.answer,
                matched_entities=matched_entities
            )

            # 6. เตรียมชุดข้อความตอบกลับ (Messages List)
            # เรียงลำดับให้ "ข้อความเนื้อหาอธิบายคำตอบ" อยู่ด้านบน และ "การ์ดรูปภาพ (Flex Card)" อยู่ด้านล่าง
            messages_to_send = []
            quick_reply = build_contextual_quick_replies(matched_entities)

            flex_card = None
            if matched_entities:
                flex_card = build_flex_message_from_entities(matched_entities)

            if flex_card:
                # 6.1 ข้อความอธิบายเชิงลึก (อยู่ข้างบน)
                messages_to_send.append(TextSendMessage(text=formatted_reply))
                # 6.2 การ์ดรูปภาพพร้อมปุ่ม Interactive (อยู่ข้างล่าง) พร้อมแนบ Quick Reply
                flex_card.quick_reply = quick_reply
                messages_to_send.append(flex_card)
            else:
                # กรณีไม่มีการ์ดรูปภาพ ให้ส่งข้อความพร้อมแนบ Quick Reply
                messages_to_send.append(TextSendMessage(text=formatted_reply, quick_reply=quick_reply))

            # 7. ส่งข้อความตอบกลับไปยัง LINE
            line_bot_api.reply_message(
                event.reply_token,
                messages_to_send
            )
            logger.info(f"[LINE Reply Sent] Successfully replied ({len(messages_to_send)} msgs, text first, {len(matched_entities)} cards below) to {user_id}")



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


# ==========================================
# Web Application & Interactive Demo Endpoints
# ==========================================

class WebChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "web_session_default"


class WebChatResetRequest(BaseModel):
    session_id: Optional[str] = "web_session_default"


@app.get("/", response_class=HTMLResponse)
@app.get("/demo", response_class=HTMLResponse)
async def serve_demo_web_app():
    """เสิร์ฟหน้าเว็บแอปพลิเคชัน Interactive Web Chat (React + Modern Japanese Clean)"""
    web_file_path = os.path.join(os.path.dirname(__file__), "..", "web", "index.html")
    if os.path.exists(web_file_path):
        with open(web_file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Tokyo RAG Web UI is loading... Please ensure src/web/index.html exists.</h1>")


@app.post("/api/chat")
async def handle_web_chat(req: WebChatRequest):
    """
    API สำหรับ Web Chat:
    - รองรับ Multi-turn Conversation และ Query Contextualization
    - ดึงข้อมูลผ่าน Hybrid RAG (Graph + Vector + BM25)
    - ส่งกลับผลลัพธ์คำตอบ, เมตริก Telemetry (Intent, Latency, Graph Path, Citations) และการ์ดสถานที่จริง
    """
    query = req.message.strip()
    session_id = req.session_id or "web_session_default"

    if not query:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    session_mgr = get_session_manager()
    rag = get_rag_service()

    # 1. จัดการคำถามต่อเนื่อง (Query Contextualization)
    resolved_query, hint = session_mgr.resolve_contextual_query(
        user_id=session_id,
        current_query=query
    )

    # 2. ค้นคืนข้อมูลผ่าน RAG Service
    response = rag.answer_query(resolved_query, mode="gemini")

    # 3. ตรวจจับ Entity สถานที่จริงเพื่อแสดงการ์ดภาพ
    matched_entities = find_matched_entities(
        text=response.answer,
        citations=response.citations,
        query=resolved_query
    )

    # 4. บันทึก Session
    session_mgr.update_session(
        user_id=session_id,
        query=query,
        resolved_query=resolved_query,
        answer=response.answer,
        matched_entities=matched_entities
    )

    return {
        "status": "success",
        "query": query,
        "resolved_query": resolved_query,
        "answer": response.answer,
        "intent": response.intent,
        "citations": response.citations,
        "latency_sec": response.latency_sec,
        "mode_used": response.mode_used,
        "model_name": response.model_name,
        "graph_context": response.graph_context,
        "cards": matched_entities
    }


@app.post("/api/chat/reset")
async def reset_web_session(req: WebChatResetRequest):
    """ล้างประวัติการสนทนาของ Session"""
    session_id = req.session_id or "web_session_default"
    session_mgr = get_session_manager()
    if session_id in session_mgr.sessions:
        del session_mgr.sessions[session_id]
    return {"status": "success", "message": f"Session '{session_id}' cleared"}


