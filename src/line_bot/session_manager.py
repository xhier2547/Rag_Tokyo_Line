"""
src/line_bot/session_manager.py
================================
ระบบจัดการบริบทการสนทนาต่อเนื่อง (Multi-turn Conversation Session Manager)
สำหรับ Tokyo Smart Transit & Tourism LINE Bot

หน้าที่หลัก:
1. จดจำบริบทการสนทนาของผู้ใช้แต่ละคน (User Session) แยกตาม LINE User ID
2. บันทึกคำถามล่าสุด, คำตอบล่าสุด, สถานีที่กล่าวถึง, และสถานที่/โรงแรมเป้าหมาย
3. วิเคราะห์คำถามต่อเนื่อง (Follow-up Query Resolution) เช่น:
   - Turn 1: "แนะนำโรงแรมใกล้สถานี Shibuya" (เป้าหมาย: Shibuya / Shibuya Stream Excel Hotel)
   - Turn 2: "แล้วถ้าฉันอยู่ที่กินซ่า ต้องไปอย่างไร"
   -> แปลงเป็น: "เดินทางจากสถานีกินซ่า ไปยังโรงแรม ชิบูย่า สตรีม เอ็กเซล โฮเทล โทคิว ที่สถานี Shibuya ต้องไปอย่างไร"
4. ล้าง Session อัตโนมัติเมื่อหมดอายุ (TTL ค่าเริ่มต้น 20 นาที)
"""

import time
import re
import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class UserSession:
    user_id: str
    last_query: str = ""
    last_resolved_query: str = ""
    last_answer: str = ""
    last_target_station: Optional[str] = None
    last_target_place: Optional[str] = None
    last_entities: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class SessionManager:
    """
    ตัวจัดการ Session การสนทนาของผู้ใช้ในหน่วยความจำ (In-Memory Session Store)
    """

    def __init__(self, session_ttl_sec: int = 1200):
        self.session_ttl_sec = session_ttl_sec
        self.sessions: Dict[str, UserSession] = {}

    def get_or_create_session(self, user_id: str) -> UserSession:
        """ดึง Session เดิมหรือสร้างใหม่หากไม่มีหรือหมดอายุ"""
        now = time.time()
        if user_id in self.sessions:
            sess = self.sessions[user_id]
            if (now - sess.timestamp) <= self.session_ttl_sec:
                return sess
            else:
                logger.info(f"[SessionManager] Session หมดอายุสำหรับ User: {user_id}")

        new_sess = UserSession(user_id=user_id, timestamp=now)
        self.sessions[user_id] = new_sess
        return new_sess

    def update_session(
        self,
        user_id: str,
        query: str,
        resolved_query: str,
        answer: str,
        matched_entities: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        อัปเดตข้อมูล Session ล่าสุดหลังจากการประมวลผลคำตอบเสร็จสิ้น
        """
        sess = self.get_or_create_session(user_id)
        sess.last_query = query
        sess.last_resolved_query = resolved_query
        sess.last_answer = answer
        sess.timestamp = time.time()
        sess.last_entities = matched_entities or []

        # สกัดสถานีเป้าหมายล่าสุด
        station_match = re.search(r'(?:สถานี|station)\s*([A-Za-zก-๙]+)', query, re.IGNORECASE)
        if not station_match:
            station_match = re.search(r'(?:สถานี|station)\s*([A-Za-zก-๙]+)', answer, re.IGNORECASE)
        if station_match:
            sess.last_target_station = station_match.group(1).strip()

        # สกัดสถานที่/โรงแรมเป้าหมายล่าสุดจาก matched_entities
        if matched_entities:
            top_entity = matched_entities[0]
            sess.last_target_place = top_entity.get("name_th", "")
            if top_entity.get("nearest_station"):
                sess.last_target_station = re.sub(r'สถานี', '', top_entity["nearest_station"]).strip()

    def resolve_contextual_query(
        self,
        user_id: str,
        current_query: str
    ) -> Tuple[str, Optional[str]]:
        """
        วิเคราะห์คำถามของผู้ใช้ หากเป็นคำถามต่อเนื่องที่มีการอ้างอิงถึงหัวข้อเดิม (เช่น ถามวิธีเดินทางจากจุดใหม่)
        จะทำการขยายบริบทให้สมบูรณ์ (Query Contextualization)

        Returns:
            Tuple[resolved_query, context_hint]
        """
        sess = self.get_or_create_session(user_id)
        clean_q = current_query.strip().lower()

        # ถ้าไม่มีประวัติคำถามก่อนหน้า ให้ใช้คำถามเดิมทันที
        if not sess.last_query or not (sess.last_target_station or sess.last_target_place):
            return current_query, None

        # คำบ่งชี้ว่าเป็นคำถามต่อเนื่องหรือถามการเดินทางต่อ
        followup_cues = [
            "แล้วถ้า", "แล้ว", "ถ้าฉัน", "ถ้าผม", "ถ้าอยู่", "ตอนนี้อยู่",
            "ต้องไปอย่างไร", "ไปยังไง", "เดินทางยังไง", "ไปที่นั่นยังไง",
            "เดินทางอย่างไร", "นั่งสายอะไร", "ไปอย่างไร", "ค่าเดินทางเท่าไหร่",
            "ไปต่อยังไง", "แล้วโรงแรมนี้", "แล้วที่นั่น"
        ]
        is_followup = any(cue in clean_q for cue in followup_cues)

        # ตรวจสอบว่าคำถามปัจจุบันระบุสถานที่หรือสถานีต้นทางใหม่หรือไม่
        # เช่น "อยู่ที่กินซ่า", "จากกินซ่า", "อยู่ชินจูกุ"
        origin_stations = {
            "กินซ่า": "สถานีกินซ่า (Ginza)",
            "ginza": "สถานีกินซ่า (Ginza)",
            "ชินจูกุ": "สถานีชินจูกุ (Shinjuku)",
            "shinjuku": "สถานีชินจูกุ (Shinjuku)",
            "ชิบูย่า": "สถานีชิบูย่า (Shibuya)",
            "shibuya": "สถานีชิบูย่า (Shibuya)",
            "โตเกียว": "สถานีโตเกียว (Tokyo)",
            "tokyo": "สถานีโตเกียว (Tokyo)",
            "อุเอโนะ": "สถานีอุเอโนะ (Ueno)",
            "ueno": "สถานีอุเอโนะ (Ueno)",
            "อาซากุสะ": "สถานีอาซากุสะ (Asakusa)",
            "asakusa": "สถานีอาซากุสะ (Asakusa)",
            "อากิฮาบาระ": "สถานีอากิฮาบาระ (Akihabara)",
            "akihabara": "สถานีอากิฮาบาระ (Akihabara)",
            "รปปงงิ": "สถานีรปปงงิ (Roppongi)",
            "roppongi": "สถานีรปปงงิ (Roppongi)",
            "โอไดบะ": "สถานีโอไดบะ (Odaiba)",
            "odaiba": "สถานีโอไดบะ (Odaiba)",
            "ฮาราจูกุ": "สถานีฮาราจูกุ (Harajuku)",
            "harajuku": "สถานีฮาราจูกุ (Harajuku)",
            "โทโยสุ": "สถานีโทโยสุ (Toyosu)",
            "toyosu": "สถานีโทโยสุ (Toyosu)",
            "โอชิอาเกะ": "สถานีโอชิอาเกะ (Oshiage)",
            "oshiage": "สถานีโอชิอาเกะ (Oshiage)",
            "อิเคะบุคุโระ": "สถานีอิเคะบุคุโระ (Ikebukuro)",
            "ikebukuro": "สถานีอิเคะบุคุโระ (Ikebukuro)",
            "ชินากาวะ": "สถานีชินากาวะ (Shinagawa)",
            "shinagawa": "สถานีชินากาวะ (Shinagawa)",
            "สึกิจิ": "สถานีสึกิจิ (Tsukiji)",
            "tsukiji": "สถานีสึกิจิ (Tsukiji)",
            "ฮามามัตสึโจ": "สถานีฮามามัตสึโจ (Hamamatsucho)",
            "hamamatsucho": "สถานีฮามามัตสึโจ (Hamamatsucho)"
        }

        detected_origin = None
        for key, display_name in origin_stations.items():
            if key in clean_q and any(p in clean_q for p in ["อยู่", "จาก", "เริ่ม"]):
                detected_origin = display_name
                break

        # กรณี 1: ผู้ใช้ระบุตำแหน่งต้นทางใหม่ และถามวิธีเดินทาง (เช่น "แล้วถ้าฉันอยู่ที่กินซ่า ต้องไปอย่างไร")
        # โดยไม่ได้ระบุปลายทางใหม่ในคำถามนี้ -> ปลายทางคือหัวข้อเดิมจากคำถามก่อนหน้า
        is_transit_how_to = any(k in clean_q for k in ["ต้องไปอย่างไร", "ไปยังไง", "เดินทางยังไง", "ไปอย่างไร", "เดินทางไปอย่างไร", "นั่งสายอะไร"])

        if is_followup and detected_origin and is_transit_how_to:
            dest_parts = []
            if sess.last_target_place:
                dest_parts.append(sess.last_target_place)
            if sess.last_target_station:
                dest_parts.append(f"สถานี {sess.last_target_station}")

            dest_str = " ".join(dest_parts)
            resolved_query = f"เดินทางจาก {detected_origin} ไปยัง {dest_str} ต้องไปอย่างไรและใช้สายรถไฟอะไร"
            context_hint = f"(คำถามต่อเนื่อง: ผู้ใช้ถามต่อจาก '{sess.last_query}' โดยปัจจุบันอยู่ที่ {detected_origin} และต้องการเดินทางไปยัง {dest_str})"
            logger.info(f"[SessionManager] Resolved Contextual Query: '{current_query}' -> '{resolved_query}'")
            return resolved_query, context_hint

        # กรณี 2: ผู้ใช้ถามคำถามเดินทางสั้นๆ เช่น "แล้วไปยังไง", "เดินทางยังไง"
        if is_followup and is_transit_how_to and not detected_origin:
            target_str = sess.last_target_place or sess.last_target_station
            if target_str:
                resolved_query = f"การเดินทางไปยัง {target_str} ต้องเดินทางอย่างไรและมีสายรถไฟอะไรบ้าง"
                context_hint = f"(คำถามต่อเนื่อง: ผู้ใช้สอบถามเส้นทางไปยัง {target_str})"
                return resolved_query, context_hint

        return current_query, None


# Global Session Manager Singleton
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
