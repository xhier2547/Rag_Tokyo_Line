"""
src/line_bot/rich_menu_creator.py
=================================
โมดูลสร้างรูปภาพ Rich Menu และลงทะเบียน Rich Menu กับ LINE Messaging API
(สำหรับโปรเจกต์ Tokyo Smart Transit & Tourism Hybrid Graph RAG)

ปุ่มทั้ง 6 เมนู:
1. 🗼 แนะนำสถานที่ฮิต (Top Landmarks)
2. ⛩️ วัด & วัฒนธรรม (Temples & Shrines)
3. 🚆 เส้นทางรถไฟ (Train & Transit)
4. 🍣 ตลาด & ของกิน (Food & Markets)
5. 🎌 Anime & ช้อปปิ้ง (Anime & Pop Culture)
6. 🗺️ จัดทริป 1 วัน (1-Day Itinerary)
"""

import os
import io
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

from linebot import LineBotApi
from linebot.models import (
    RichMenu,
    RichMenuSize,
    RichMenuArea,
    RichMenuBounds,
    MessageAction
)

load_dotenv()


def get_windows_font(font_name: str, size: int):
    """โหลดฟอนต์ระบบ Windows สำหรับเรนเดอร์ภาษาไทย"""
    windir = os.environ.get("WINDIR", "C:\\Windows")
    font_path = os.path.join(windir, "Fonts", font_name)
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def generate_rich_menu_image(output_path: str = "data/rich_menu.png") -> str:
    """
    สร้างรูปภาพ Rich Menu ขนาดมาตรฐาน 2500 x 1686 พิกเซล
    แบ่งเป็น 6 ช่อง (2 แถว x 3 คอลัมน์) สีสันทันสมัยระดับพรีเมียม
    """
    width = 2500
    height = 1686
    col_w = width // 3     # 833 px
    row_h = height // 2    # 843 px

    img = Image.new("RGB", (width, height), color="#1E293B")
    draw = ImageDraw.Draw(img)

    # โหลดฟอนต์ภาษาไทยและอังกฤษ
    title_font = get_windows_font("tahoma.ttf", 64)
    sub_font = get_windows_font("segoeui.ttf", 44)
    emoji_font = get_windows_font("seguiemj.ttf", 90)

    # รายละเอียดทั้ง 6 ช่อง
    cells = [
        # แถวบน
        {
            "col": 0, "row": 0,
            "bg": "#0F172A", "accent": "#38BDF8",
            "icon": "🗼", "title": "สถานที่ท่องเที่ยวยอดนิยม", "sub": "Top Landmarks & Views"
        },
        {
            "col": 1, "row": 0,
            "bg": "#1E293B", "accent": "#F43F5E",
            "icon": "⛩️", "title": "วัด & ศาลเจ้าเก่าแก่", "sub": "Historic Temples & Shrines"
        },
        {
            "col": 2, "row": 0,
            "bg": "#0F172A", "accent": "#10B981",
            "icon": "🚆", "title": "ค้นหาเส้นทางรถไฟ", "sub": "Transit & Duration Query"
        },
        # แถวล่าง
        {
            "col": 0, "row": 1,
            "bg": "#1E293B", "accent": "#F59E0B",
            "icon": "🍣", "title": "ตลาดอาหาร & ย่านกิน", "sub": "Street Food & Tsukiji Market"
        },
        {
            "col": 1, "row": 1,
            "bg": "#0F172A", "accent": "#A855F7",
            "icon": "🎌", "title": "Anime & Akihabara", "sub": "Gaming & Pop Culture Tour"
        },
        {
            "col": 2, "row": 1,
            "bg": "#1E293B", "accent": "#EC4899",
            "icon": "🗺️", "title": "ช่วยจัดทริป 1 วัน", "sub": "1-Day Tokyo Itinerary"
        }
    ]

    for c in cells:
        x0 = c["col"] * col_w
        y0 = c["row"] * row_h
        x1 = x0 + col_w
        y1 = y0 + row_h

        # วาดพื้นหลังกล่อง
        draw.rectangle([x0, y0, x1, y1], fill=c["bg"])

        # วาดเส้นขอบไฮไลต์ด้านบนของแต่ละช่อง
        draw.line([(x0, y0), (x1, y0)], fill=c["accent"], width=6)
        draw.line([(x0, y0), (x0, y1)], fill="#334155", width=2)

        # คำนวณตำแหน่งกึ่งกลาง
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2

        # วาดไอคอน
        draw.text((cx, cy - 140), c["icon"], fill="#FFFFFF", font=emoji_font, anchor="mm")

        # วาดชื่อภาษาไทย
        draw.text((cx, cy + 40), c["title"], fill="#FFFFFF", font=title_font, anchor="mm")

        # วาดคำอธิบายภาษาอังกฤษ
        draw.text((cx, cy + 130), c["sub"], fill=c["accent"], font=sub_font, anchor="mm")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"[RichMenuCreator] บันทึกรูปภาพ Rich Menu ขนาด {width}x{height} ลงที่ '{output_path}' เรียบร้อย")
    return output_path


def create_rich_menu_object() -> RichMenu:
    """สร้าง RichMenu Object ตามโครงสร้างของ LINE SDK"""
    width = 2500
    height = 1686
    col_w = width // 3
    row_h = height // 2

    areas = [
        # ปุ่ม 1: สถานที่ท่องเที่ยวฮิต
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=col_w, height=row_h),
            action=MessageAction(text="แนะนำ 5 สถานที่ท่องเที่ยวยอดนิยมใน Tokyo")
        ),
        # ปุ่ม 2: วัดและศาลเจ้า
        RichMenuArea(
            bounds=RichMenuBounds(x=col_w, y=0, width=col_w, height=row_h),
            action=MessageAction(text="แนะนำวัดและศาลเจ้าที่มีชื่อเสียงใน Tokyo พร้อมประวัติ")
        ),
        # ปุ่ม 3: ค้นหาเส้นทางรถไฟ
        RichMenuArea(
            bounds=RichMenuBounds(x=col_w * 2, y=0, width=col_w, height=row_h),
            action=MessageAction(text="เดินทางจาก Shinjuku ไป Shibuya ใช้เวลาเดินทางกี่นาที และสายอะไร?")
        ),
        # ปุ่ม 4: ตลาดอาหารและของกิน
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=row_h, width=col_w, height=row_h),
            action=MessageAction(text="Tsukiji Outer Market มีอะไรน่าสนใจ และเดินทางไปยังไง?")
        ),
        # ปุ่ม 5: Anime & Akihabara
        RichMenuArea(
            bounds=RichMenuBounds(x=col_w, y=row_h, width=col_w, height=row_h),
            action=MessageAction(text="Akihabara มีสถานที่อะไรที่เหมาะกับแฟน Anime และ Gaming?")
        ),
        # ปุ่ม 6: ช่วยจัดทริป 1 วัน
        RichMenuArea(
            bounds=RichMenuBounds(x=col_w * 2, y=row_h, width=col_w, height=row_h),
            action=MessageAction(text="ช่วยจัดทริป Tokyo 1 วันสำหรับคนมาครั้งแรกให้หน่อย")
        ),
    ]

    rich_menu = RichMenu(
        size=RichMenuSize(width=width, height=height),
        selected=True,
        name="Tokyo Tourism RAG Rich Menu",
        chat_bar_text="🗼 เมนูท่องเที่ยวและรถไฟโตเกียว",
        areas=areas
    )
    return rich_menu


def setup_default_rich_menu(channel_access_token: Optional[str] = None) -> Optional[str]:
    """
    สร้างและตั้งค่า Rich Menu ให้เป็น Default สำหรับผู้ใช้ทุกคน
    """
    token = channel_access_token or os.getenv("CHANNEL_ACCESS_TOKEN")
    if not token:
        print("⚠️ ไม่พบ CHANNEL_ACCESS_TOKEN ในไฟล์ .env ไม่สามารถลงทะเบียน Rich Menu กับ LINE API ได้")
        return None

    line_bot_api = LineBotApi(token)

    try:
        # 1. สร้างรูปภาพ Rich Menu ก่อน
        image_path = generate_rich_menu_image()

        # 2. ลบ Rich Menu เก่าเพื่อไม่ให้ค้าง
        old_menus = line_bot_api.get_rich_menu_list()
        for m in old_menus:
            if m.name == "Tokyo Tourism RAG Rich Menu":
                line_bot_api.delete_rich_menu(m.rich_menu_id)
                print(f"[RichMenuCreator] ลบ Rich Menu เดิม: {m.rich_menu_id}")

        # 3. สร้าง Rich Menu ใหม่
        rich_menu_obj = create_rich_menu_object()
        rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_obj)
        print(f"[RichMenuCreator] สร้าง Rich Menu ใหม่สำเร็จ ID: {rich_menu_id}")

        # 4. อัปโหลดรูปภาพ
        with open(image_path, "rb") as f:
            line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)
        print("[RichMenuCreator] อัปโหลดรูปภาพ Rich Menu ไปยัง LINE สำเร็จ!")

        # 5. ตั้งเป็น Default Menu ให้ทุกคนเห็นทันที
        line_bot_api.set_default_rich_menu(rich_menu_id)
        print("[RichMenuCreator] ตั้งค่า Rich Menu เป็น Default ให้กับผู้ใช้ทุกคนเรียบร้อย! 🎉")
        return rich_menu_id

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการตั้งค่า Rich Menu: {e}")
        return None


if __name__ == "__main__":
    setup_default_rich_menu()
