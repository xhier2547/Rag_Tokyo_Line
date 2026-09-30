"""
src/line_bot/media_catalog.py
=============================
โมดูลแคตตาล็อกรูปภาพและข้อมูลมัลติมีเดีย (Media Catalog) สำหรับโตเกียว
รวบรวมรูปภาพความคมชัดสูง (Direct CDN Image URLs) สำหรับ 20 สถานที่ และ 10 โรงแรม
พร้อมฟังก์ชันตรวจจับ Entity (Place / Hotel) จากคำตอบเพื่อนำไปสร้าง Flex Cards
"""

import re
from typing import Dict, List, Any, Optional

DEFAULT_TOKYO_IMAGE = "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800&q=80"

PLACE_MEDIA_CATALOG: Dict[str, Dict[str, Any]] = {
    "P_SENSOJI": {
        "id": "P_SENSOJI",
        "name_th": "วัดเซ็นโซจิ (วัดอาซากุสะ)",
        "name_en": "Senso-ji Temple",
        "image_url": "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=800&q=80",
        "category": "⛩️ วัดและศาลเจ้า",
        "ward": "Taito",
        "nearest_station": "สถานี Asakusa",
        "walk_time_min": 5,
        "keywords": ["เซ็นโซจิ", "อาซากุสะ", "senso-ji", "sensoji", "asakusa", "โคมแดง", "คามินาริโมง"]
    },
    "P_TOKYO_SKYTREE": {
        "id": "P_TOKYO_SKYTREE",
        "name_th": "โตเกียวสกายทรี (Tokyo Skytree)",
        "name_en": "Tokyo Skytree",
        "image_url": "https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=800&q=80",
        "category": "🗼 จุดชมวิวและแลนด์มาร์ก",
        "ward": "Sumida",
        "nearest_station": "สถานี Oshiage (Skytree)",
        "walk_time_min": 2,
        "keywords": ["สกายทรี", "skytree", "โตเกียวสกายทรี", "oshiage", "solamachi"]
    },
    "P_SHIBUYA_CROSSING": {
        "id": "P_SHIBUYA_CROSSING",
        "name_th": "ห้าแยกชิบูย่าและรูปปั้นฮาจิโกะ",
        "name_en": "Shibuya Crossing & Hachiko",
        "image_url": "https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=800&q=80",
        "category": "🚶 แลนด์มาร์กและถนนคนเดิน",
        "ward": "Shibuya",
        "nearest_station": "สถานี Shibuya",
        "walk_time_min": 1,
        "keywords": ["ชิบูย่า", "ชิบูยะ", "shibuya", "crossing", "ฮาจิโกะ", "hachiko", "ห้าแยก"]
    },
    "P_MEIJI_JINGU": {
        "id": "P_MEIJI_JINGU",
        "name_th": "ศาลเจ้าเมจิ (Meiji Jingu Shrine)",
        "name_en": "Meiji Jingu Shrine",
        "image_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=800&q=80",
        "category": "⛩️ ศาลเจ้าชินโตโบราณ",
        "ward": "Shibuya",
        "nearest_station": "สถานี Harajuku",
        "walk_time_min": 3,
        "keywords": ["เมจิ", "meiji", "ศาลเจ้าเมจิ", "meiji jingu"]
    },
    "P_TOKYO_TOWER": {
        "id": "P_TOKYO_TOWER",
        "name_th": "โตเกียวทาวเวอร์ (Tokyo Tower)",
        "name_en": "Tokyo Tower",
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800&q=80",
        "category": "🗼 หอคอยคลาสสิกแลนด์มาร์ก",
        "ward": "Minato",
        "nearest_station": "สถานี Hamamatsucho",
        "walk_time_min": 15,
        "keywords": ["โตเกียวทาวเวอร์", "tokyo tower", "หอคอยโตเกียว", "hamamatsucho"]
    },
    "P_SHINJUKU_GYOEN": {
        "id": "P_SHINJUKU_GYOEN",
        "name_th": "สวนสาธารณะชินจูกุเกียวเอ็น",
        "name_en": "Shinjuku Gyoen National Garden",
        "image_url": "https://images.unsplash.com/photo-1578637387939-43c525550085?w=800&q=80",
        "category": "🌸 สวนธรรมชาติและซากุระ",
        "ward": "Shinjuku",
        "nearest_station": "สถานี Shinjuku-gyoemmae",
        "walk_time_min": 5,
        "keywords": ["ชินจูกุเกียวเอ็น", "gyoen", "shinjuku gyoen", "สวนชินจูกุ"]
    },
    "P_AKIHABARA_ELECTRIC": {
        "id": "P_AKIHABARA_ELECTRIC",
        "name_th": "ย่านอนิเมะและเครื่องใช้ไฟฟ้าอากิฮาบาระ",
        "name_en": "Akihabara Electric Town",
        "image_url": "https://images.unsplash.com/photo-1509099836639-18ba1795216d?w=800&q=80",
        "category": "🎮 ช้อปปิ้ง อนิเมะ & ไอที",
        "ward": "Chiyoda",
        "nearest_station": "สถานี Akihabara",
        "walk_time_min": 1,
        "keywords": ["อากิฮาบาระ", "akihabara", "akiba", "อนิเมะ", "ฟิกเกอร์", "เมดคาเฟ่"]
    },
    "P_TSUKIJI_OUTER": {
        "id": "P_TSUKIJI_OUTER",
        "name_th": "ตลาดปลาสึกิจิ (Tsukiji Outer Market)",
        "name_en": "Tsukiji Outer Market",
        "image_url": "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?w=800&q=80",
        "category": "🍣 สตรีทฟู้ดและอาหารทะเลสด",
        "ward": "Chuo",
        "nearest_station": "สถานี Tsukiji",
        "walk_time_min": 4,
        "keywords": ["สึกิจิ", "ซึกิจิ", "tsukiji", "ตลาดปลาสึกิจิ", "ซูชิ", "ไข่หวาน"]
    },
    "P_UENO_PARK": {
        "id": "P_UENO_PARK",
        "name_th": "สวนอุเอโนะและพิพิธภัณฑ์แห่งชาติ",
        "name_en": "Ueno Park & National Museum",
        "image_url": "https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&q=80",
        "category": "🏛️ วัฒนธรรม พิพิธภัณฑ์ & สวนสัตว์",
        "ward": "Taito",
        "nearest_station": "สถานี Ueno",
        "walk_time_min": 2,
        "keywords": ["อุเอโนะ", "ueno", "สวนอุเอโนะ", "ueno park", "พิพิธภัณฑ์สถานแห่งชาติ"]
    },
    "P_ROPPONGI_HILLS": {
        "id": "P_ROPPONGI_HILLS",
        "name_th": "รปปงงิฮิลส์และจุดชมวิวโตเกียวซิตี้วิว",
        "name_en": "Roppongi Hills & Tokyo City View",
        "image_url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80",
        "category": "✨ จุดชมวิวระฟ้า & หอศิลป์",
        "ward": "Minato",
        "nearest_station": "สถานี Roppongi",
        "walk_time_min": 3,
        "keywords": ["รปปงงิ", "roppongi", "รปปงงิฮิลส์", "roppongi hills", "mori tower", "city view"]
    },
    "P_GINZA_SIX": {
        "id": "P_GINZA_SIX",
        "name_th": "ย่านช้อปปิ้งกินซ่าและห้าง GINZA SIX",
        "name_en": "Ginza Shopping & GINZA SIX",
        "image_url": "https://images.unsplash.com/photo-1554797589-7241bb691973?w=800&q=80",
        "category": "🛍️ แฟชั่นแบรนด์เนมระดับโลก",
        "ward": "Chuo",
        "nearest_station": "สถานี Ginza",
        "walk_time_min": 2,
        "keywords": ["กินซ่า", "ginza", "ginza six", "ห้างกินซ่า"]
    },
    "P_ODAIBA_GUNDAM": {
        "id": "P_ODAIBA_GUNDAM",
        "name_th": "โอไดบะและหุ่นยนต์กันดั้มยักษ์ยูนิคอร์น",
        "name_en": "Odaiba & Unicorn Gundam Statue",
        "image_url": "https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80",
        "category": "🤖 กันดั้มริมอ่าว & เมืองบันเทิง",
        "ward": "Minato",
        "nearest_station": "สถานี Odaiba-Kaihinkoen",
        "walk_time_min": 5,
        "keywords": ["โอไดบะ", "odaiba", "กันดั้ม", "gundam", "rainbow bridge", "divercity"]
    },
    "P_IMPERIAL_PALACE": {
        "id": "P_IMPERIAL_PALACE",
        "name_th": "พระราชวังอิมพีเรียลโตเกียว (Imperial Palace)",
        "name_en": "Tokyo Imperial Palace",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/c/ca/Imperial_Palace_Tokyo_Nijubashi_Bridge.JPG",
        "category": "🏯 พระราชวังโบราณ & ปราสาทเอโดะ",
        "ward": "Chiyoda",
        "nearest_station": "สถานี Tokyo",
        "walk_time_min": 10,
        "keywords": ["อิมพีเรียล", "imperial", "พระราชวังอิมพีเรียล", "ปราสาทเอโดะ", "นิจูบาชิ"]
    },
    "P_TEAMLAB_PLANETS": {
        "id": "P_TEAMLAB_PLANETS",
        "name_th": "พิพิธภัณฑ์ศิลปะดิจิทัล teamLab Planets",
        "name_en": "teamLab Planets TOKYO",
        "image_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&q=80",
        "category": "✨ ศิลปะดิจิทัล Immersive Art",
        "ward": "Koto",
        "nearest_station": "สถานี Toyosu",
        "walk_time_min": 10,
        "keywords": ["teamlab", "ทีมแล็บ", "teamlab planets", "ศิลปะดิจิทัล"]
    },
    "P_AMEYOKO": {
        "id": "P_AMEYOKO",
        "name_th": "ตลาดอะเมโยโกะ (Ameyoko Market)",
        "name_en": "Ameyoko Shopping Street",
        "image_url": "https://images.unsplash.com/photo-1551641506-ee5bf4cb45f1?w=800&q=80",
        "category": "🍢 ตลาดกลางแจ้ง & สตรีทฟู้ด",
        "ward": "Taito",
        "nearest_station": "สถานี Ueno",
        "walk_time_min": 2,
        "keywords": ["อะเมโยโกะ", "ameyoko", "ตลาดอะเมโยโกะ", "ถนนคนเดินอุเอโนะ"]
    },
    "P_TAKESHITA_STREET": {
        "id": "P_TAKESHITA_STREET",
        "name_th": "ถนนทาเคชิตะ ย่านฮาราจูกุ",
        "name_en": "Takeshita Street Harajuku",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Takeshita_Street_in_Harajuku.jpg/1280px-Takeshita_Street_in_Harajuku.jpg",
        "category": "🥞 แฟชั่นวัยรุ่น เครป & คาวาอี้",
        "ward": "Shibuya",
        "nearest_station": "สถานี Harajuku",
        "walk_time_min": 1,
        "keywords": ["ทาเคชิตะ", "takeshita", "ฮาราจูกุ", "harajuku", "เครป"]
    },
    "P_HAMARIKYU_GARDENS": {
        "id": "P_HAMARIKYU_GARDENS",
        "name_th": "สวนฮามาริคิว (Hamarikyu Gardens)",
        "name_en": "Hamarikyu Gardens",
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800&q=80",
        "category": "🍵 สวนโชกุนริมอ่าว & โรงน้ำชา",
        "ward": "Chuo",
        "nearest_station": "สถานี Shimbashi",
        "walk_time_min": 10,
        "keywords": ["ฮามาริคิว", "hamarikyu", "สวนฮามาริคิว", "โรงน้ำชา"]
    },
    "P_TOKYO_DOME_CITY": {
        "id": "P_TOKYO_DOME_CITY",
        "name_th": "โตเกียวโดมซิตี้และสปา LaQua",
        "name_en": "Tokyo Dome City & Spa LaQua",
        "image_url": "https://images.unsplash.com/photo-1513407030348-c983a97b98d8?w=800&q=80",
        "category": "🎡 สวนสนุก โดม & ออนเซ็น",
        "ward": "Bunkyo",
        "nearest_station": "สถานี Korakuen",
        "walk_time_min": 3,
        "keywords": ["โตเกียวโดม", "tokyo dome", "laqua", "ลาคัว", "korakuen"]
    },
    "P_TOYOSU_MARKET": {
        "id": "P_TOYOSU_MARKET",
        "name_th": "ตลาดปลาโทโยสุและเซ็นเคียคุบันไร",
        "name_en": "Toyosu Market & Senkyaku Banrai",
        "image_url": "https://images.unsplash.com/photo-1611143669185-af224c5e3252?w=800&q=80",
        "category": "🐟 ตลาดประมูลปลา & เอโดะออนเซ็น",
        "ward": "Koto",
        "nearest_station": "สถานี Shijo-mae",
        "walk_time_min": 2,
        "keywords": ["โทโยสุ", "toyosu", "ตลาดปลาโทโยสุ", "senkyaku banrai", "เซ็นเคียคุบันไร"]
    },
    "P_OMOTESANDO_HILLS": {
        "id": "P_OMOTESANDO_HILLS",
        "name_th": "ถนนช้อปปิ้งโอโมเตะซันโดฮิลส์",
        "name_en": "Omotesando Boulevard & Hills",
        "image_url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80",
        "category": "☕ สถาปัตยกรรม บูทีก & คาเฟ่",
        "ward": "Shibuya",
        "nearest_station": "สถานี Omotesando",
        "walk_time_min": 2,
        "keywords": ["โอโมเตะซันโด", "omotesando", "omotesando hills", "โอโมเตะซันโดฮิลส์"]
    }
}

HOTEL_MEDIA_CATALOG: Dict[str, Dict[str, Any]] = {
    "H_GRACERY_SHINJUKU": {
        "id": "H_GRACERY_SHINJUKU",
        "name_th": "โรงแรมเกรเซอรี ชินจูกุ (Godzilla Hotel)",
        "name_en": "Hotel Gracery Shinjuku",
        "image_url": "https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800&q=80",
        "category": "🏨 โรงแรมก็อดซิลล่า คาบูกิโจ",
        "tier": "Business / Mid-Scale",
        "price_range": "3,500 - 6,500 บาท/คืน",
        "ward": "Shinjuku",
        "nearest_station": "สถานี Shinjuku",
        "walk_time_min": 5,
        "keywords": ["เกรเซอรี", "gracery", "godzilla", "ก็อดซิลล่า"]
    },
    "H_TOKYO_STATION_HOTEL": {
        "id": "H_TOKYO_STATION_HOTEL",
        "name_th": "โรงแรมเดอะ โตเกียว สเตชั่น โฮเทล (5 ดาว)",
        "name_en": "The Tokyo Station Hotel",
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80",
        "category": "👑 โรงแรมหรูประวัติศาสตร์ในสถานี",
        "tier": "Luxury",
        "price_range": "15,000 - 30,000 บาท/คืน",
        "ward": "Chiyoda",
        "nearest_station": "สถานี Tokyo",
        "walk_time_min": 1,
        "keywords": ["โตเกียวสเตชั่นโฮเทล", "tokyo station hotel"]
    },
    "H_SHIBUYA_STREAM_EXCEL": {
        "id": "H_SHIBUYA_STREAM_EXCEL",
        "name_th": "ชิบูย่า สตรีม เอ็กเซล โฮเทล โทคิว",
        "name_en": "Shibuya Stream Excel Hotel Tokyu",
        "image_url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&q=80",
        "category": "🏨 ดีไซน์โฮเทลเชื่อมตรงสถานี",
        "tier": "Business / Mid-Scale",
        "price_range": "5,500 - 9,500 บาท/คืน",
        "ward": "Shibuya",
        "nearest_station": "สถานี Shibuya",
        "walk_time_min": 2,
        "keywords": ["shibuya stream", "ชิบูย่าสตรีม", "ชิบูย่า สตรีม", "excel hotel", "เอ็กเซล โฮเทล", "สตรีม เอ็กเซล", "shibuya stream excel"]
    },
    "H_ASAKUSA_VIEW": {
        "id": "H_ASAKUSA_VIEW",
        "name_th": "โรงแรมอาซากุสะ วิว โฮเทล",
        "name_en": "Asakusa View Hotel",
        "image_url": "https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80",
        "category": "🗼 โรงแรมวิวสกายทรี & วัดเซ็นโซจิ",
        "tier": "Mid-Scale",
        "price_range": "3,000 - 6,000 บาท/คืน",
        "ward": "Taito",
        "nearest_station": "สถานี Asakusa",
        "walk_time_min": 6,
        "keywords": ["อาซากุสะวิว", "asakusa view", "อาซากุสะ วิว"]
    },
    "H_DORM_INN_AKIHABARA": {
        "id": "H_DORM_INN_AKIHABARA",
        "name_th": "ดอร์มี อินน์ อากิฮาบาระ (ออนเซ็นดาดฟ้า)",
        "name_en": "Dormy Inn Akihabara Hot Springs",
        "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80",
        "category": "♨️ ออนเซ็นฟรี & ราเมนรอบดึก",
        "tier": "Budget / Mid-Scale",
        "price_range": "2,800 - 4,800 บาท/คืน",
        "ward": "Chiyoda",
        "nearest_station": "สถานี Akihabara",
        "walk_time_min": 5,
        "keywords": ["ดอร์มี", "dormy inn", "dormy", "ดอร์มี อินน์"]
    }
}


def find_matched_entities(
    text: str,
    citations: Optional[List[str]] = None,
    query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    ตรวจจับสถานที่ท่องเที่ยว (Places) หรือโรงแรม (Hotels) ที่ปรากฏในข้อความคำตอบ หรือในรายการ Citations
    - รักษาลำดับการแนะนำตามที่ปรากฏในคำตอบของ AI (First Mention Order)
    - หากผู้ใช้ถามจากตำแหน่งปัจจุบัน เช่น "อยู่ที่ชิบูย่า จะไปไหนดี" หรือ "เดินทางจากกินซ่า ไปโรงแรมชิบูย่าสตรีม"
      จะแยกแยะตำแหน่งต้นทาง (Origin) และให้ความสำคัญกับการ์ดสถานที่ปลายทาง (Destinations) ก่อนเสมอ
    - คืนค่ารายการ Dictionary ข้อมูลสื่อสำหรับนำไปสร้าง Flex Cards (สูงสุด 3 รายการเพื่อความสวยงาม)
    """
    combined_text = (text + " " + " ".join(citations or [])).lower()
    matched_candidates: List[Dict[str, Any]] = []
    seen_ids = set()

    # ตรวจหาตำแหน่งต้นทาง (Origin) จากคำถาม เช่น "อยู่ที่...", "จาก... ไป..."
    origin_ids = set()
    if query:
        clean_q = query.lower()
        origin_text = ""
        if "จาก" in clean_q and ("ไป" in clean_q or "ถึง" in clean_q):
            m = re.search(r'(?:จาก|ออกจาก|เริ่มต้นที่)\s*(.*?)\s*(?:ไปยัง|ไป|ถึง)', clean_q)
            if m:
                origin_text = m.group(1).strip()
        elif any(k in clean_q for k in ["อยู่ที่", "ตอนนี้อยู่", "ถ้าอยู่", "หากอยู่"]):
            m = re.search(r'(?:อยู่ที่|ตอนนี้อยู่|ถ้าอยู่|หากอยู่)\s*(.*?)(?:\s*(?:จะไป|ไป|ต้องไป|มีอะไร|เที่ยว|ละ|ครับ|ค่ะ|\Z))', clean_q)
            if m:
                origin_text = m.group(1).strip()

        if origin_text:
            for pid, data in {**PLACE_MEDIA_CATALOG, **HOTEL_MEDIA_CATALOG}.items():
                for kw in data["keywords"]:
                    if kw in origin_text:
                        origin_ids.add(pid)
                        break


    all_catalog_items = [
        *[(pid, data, "place") for pid, data in PLACE_MEDIA_CATALOG.items()],
        *[(hid, data, "hotel") for hid, data in HOTEL_MEDIA_CATALOG.items()]
    ]

    for eid, data, etype in all_catalog_items:
        if eid in seen_ids:
            continue
        best_pos = None
        best_kw_len = 0
        for kw in data["keywords"]:
            pos = combined_text.find(kw)
            if pos != -1:
                # เลือกตำแหน่งที่พบแรกสุด หรือถ้าพบที่เดียวกันให้เลือกคำที่ยาวที่สุด
                if best_pos is None or pos < best_pos or (pos == best_pos and len(kw) > best_kw_len):
                    best_pos = pos
                    best_kw_len = len(kw)
        if best_pos is not None:
            matched_candidates.append({
                **data,
                "type": etype,
                "pos": best_pos,
                "kw_len": best_kw_len,
                "is_origin": eid in origin_ids
            })
            seen_ids.add(eid)

    # เรียงลำดับ: ตำแหน่งแรกสุดก่อน หากตำแหน่งเดียวกันให้คำที่ยาว/เจาะจงกว่าขึ้นก่อน
    matched_candidates.sort(key=lambda x: (x["pos"], -x["kw_len"]))

    # หากมีคำทับซ้อนกันในตำแหน่งเดียวกัน (เช่น "ชิบูย่า สตรีม" กับ "ชิบูย่า") ให้เก็บเฉพาะคำที่ยาวกว่า
    non_overlapping = []
    covered_spans = []
    for cand in matched_candidates:
        c_start = cand["pos"]
        c_end = c_start + cand["kw_len"]
        # ตรวจสอบว่าถูกคลุมโดยคำที่ยาวกว่าไปแล้วหรือไม่
        is_sub = False
        for (s, e) in covered_spans:
            if c_start >= s and c_end <= e:
                is_sub = True
                break
        if not is_sub:
            non_overlapping.append(cand)
            covered_spans.append((c_start, c_end))

    # หากมีสถานที่ปลายทางอื่นๆ ให้กรองสถานที่ต้นทาง (เช่น สถานีกินซ่า เมื่อเดินทางจากกินซ่า) ออก
    # เพื่อให้การ์ดแสดงเฉพาะสถานที่ปลายทางที่แนะนำให้เดินทางไป
    destinations = [m for m in non_overlapping if not m.get("is_origin", False)]
    if destinations:
        final_list = destinations
    else:
        final_list = non_overlapping

    # คืนค่าสูงสุด 3 รายการเพื่อไม่ให้แชตยาวเกินไป
    return final_list[:3]


