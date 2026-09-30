"""
src/line_bot/flex_cards.py
==========================
โมดูลสร้าง LINE Flex Message (Visual Cards & Carousels) พร้อมปุ่ม Interactive Actions
ตามข้อกำหนดของ LINE Messaging API และหลักการออกแบบ Modern Rich Aesthetics
"""

from typing import Dict, List, Any, Optional
from linebot.models import (
    FlexSendMessage,
    QuickReply,
    QuickReplyButton,
    MessageAction
)


def create_entity_bubble(entity: Dict[str, Any]) -> Dict[str, Any]:
    """
    สร้าง Flex Message Bubble สำหรับสถานที่ท่องเที่ยว 1 แห่ง หรือโรงแรม 1 แห่ง
    ประกอบด้วย Hero Image, Category Badge, สถานีใกล้เคียง, และปุ่ม Action ไปต่อ
    """
    name_th = entity.get("name_th", "สถานที่ในโตเกียว")
    name_en = entity.get("name_en", "")
    image_url = entity.get("image_url", "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=800&q=80")
    category = entity.get("category", "ท่องเที่ยวโตเกียว")
    nearest_station = entity.get("nearest_station", "สถานีใจกลางโตเกียว")
    walk_min = entity.get("walk_time_min", 3)
    is_hotel = entity.get("type") == "hotel"

    # Action texts เมื่อผู้ใช้กดปุ่ม
    if is_hotel:
        action_route = f"สถานีใกล้เคียงและวิธีเดินทางไป{name_th}"
        action_explore = f"ที่เที่ยวใกล้{nearest_station}"
    else:
        action_route = f"สถานีใกล้เคียงและวิธีเดินทางไป{name_th}"
        action_explore = f"ของกินแนะนำใกล้{name_th}"

    bubble: Dict[str, Any] = {
        "type": "bubble",
        "size": "mega",
        "hero": {
            "type": "image",
            "url": image_url,
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
                "type": "message",
                "label": "ดูรายละเอียด",
                "text": f"เล่าประวัติและไฮไลต์ของ {name_th} ให้ฟังหน่อย"
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": name_th,
                    "weight": "bold",
                    "size": "lg",
                    "wrap": True,
                    "color": "#1E293B"
                },
                {
                    "type": "text",
                    "text": name_en,
                    "size": "xs",
                    "color": "#64748B",
                    "wrap": True
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "spacing": "sm",
                    "margin": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": category,
                            "size": "xs",
                            "color": "#2563EB",
                            "weight": "bold",
                            "flex": 0
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "spacing": "xs",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "🚆 สถานี:",
                                    "size": "xs",
                                    "color": "#475569",
                                    "flex": 2
                                },
                                {
                                    "type": "text",
                                    "text": f"{nearest_station} (เดิน ~{walk_min} นาที)",
                                    "size": "xs",
                                    "color": "#0F172A",
                                    "weight": "bold",
                                    "flex": 5,
                                    "wrap": True
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#0284C7",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "🚆 ขอเส้นทางไปที่นี่",
                        "text": action_route[:300]
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "🍣 ของกินแถวนี้" if not is_hotel else "📍 ที่เที่ยวใกล้เคียง",
                        "text": action_explore[:300]
                    }
                }
            ]
        }
    }

    # หากเป็นโรงแรม ให้เพิ่มบรรทัดราคาลงใน Body
    if is_hotel and "price_range" in entity:
        price_text = entity["price_range"]
        bubble["body"]["contents"].append({
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "margin": "xs",
            "contents": [
                {
                    "type": "text",
                    "text": "💰 ราคา:",
                    "size": "xs",
                    "color": "#475569",
                    "flex": 2
                },
                {
                    "type": "text",
                    "text": price_text,
                    "size": "xs",
                    "color": "#16A34A",
                    "weight": "bold",
                    "flex": 5
                }
            ]
        })

    return bubble


def build_flex_message_from_entities(entities: List[Dict[str, Any]]) -> Optional[FlexSendMessage]:
    """
    สร้าง FlexSendMessage จากรายการสถานที่/โรงแรม (ถ้า 1 แห่งจะเป็น Bubble, ถ้า 2-3 แห่งจะเป็น Carousel)
    """
    if not entities:
        return None

    if len(entities) == 1:
        bubble = create_entity_bubble(entities[0])
        alt_text = f"📍 ข้อมูล {entities[0].get('name_th', 'สถานที่ท่องเที่ยว')}"
        return FlexSendMessage(alt_text=alt_text[:400], contents=bubble)
    else:
        bubbles = [create_entity_bubble(e) for e in entities[:3]]
        carousel = {
            "type": "carousel",
            "contents": bubbles
        }
        alt_text = f"📍 แนะนำ {len(bubbles)} สถานที่ในโตเกียว"
        return FlexSendMessage(alt_text=alt_text[:400], contents=carousel)


def build_contextual_quick_replies(entities: List[Dict[str, Any]]) -> QuickReply:
    """
    สร้างปุ่ม Quick Reply ไดนามิก โดยอิงจากสถานที่ที่เพิ่งตอบในคำตอบปัจจุบัน
    เพื่อให้ผู้ใช้สามารถแตะถามต่อได้อย่างเป็นธรรมชาติและสะดวกที่สุด
    """
    buttons = []

    if entities:
        main_entity = entities[0]
        name = main_entity.get("name_th", "").split("(")[0].strip()
        station = main_entity.get("nearest_station", "Shinjuku").replace("สถานี", "").strip()

        # 1. ปุ่มขอเส้นทาง
        buttons.append((f"🚆 ไป {name[:12]}", f"เดินทางไป {name} ยังไง"))
        # 2. ปุ่มของกินหรือที่เที่ยว
        if main_entity.get("type") == "hotel":
            buttons.append((f"📍 เที่ยวแถว {station[:10]}", f"ที่เที่ยวใกล้สถานี {station}"))
        else:
            buttons.append((f"🍣 ของกิน {name[:12]}", f"ของกินแนะนำใกล้ {name}"))
        # 3. ปุ่มที่พักใกล้สถานี
        buttons.append((f"🏨 ที่พัก {station[:10]}", f"แนะนำโรงแรมใกล้สถานี {station}"))
        # 4. ปุ่มจัดทริปหรือสถานที่ยอดนิยม
        buttons.append(("🗼 ที่เที่ยวฮิต", "แนะนำ 5 สถานที่ท่องเที่ยวยอดนิยมใน Tokyo"))
    else:
        # Fallback กรณีไม่มี entity เจาะจง
        buttons = [
            ("🗼 ที่เที่ยวฮิต", "แนะนำ 5 สถานที่ท่องเที่ยวยอดนิยมใน Tokyo"),
            ("⛩️ วัด Senso-ji", "วัด Sensō-ji มีประวัติและความสำคัญอย่างไร?"),
            ("🚆 รถไฟ Shinjuku", "เดินทางจาก Shinjuku ไป Shibuya ใช้สายอะไรและกี่นาที?"),
            ("🍣 ตลาดปลา Tsukiji", "Tsukiji Outer Market มีอะไรน่าสนใจ และไปยังไง?"),
            ("🏨 แนะนำโรงแรม", "แนะนำโรงแรมใกล้สถานีชินจูกุให้หน่อย มีที่ไหนเด่นๆ บ้าง"),
            ("🗺️ ทริป 1 วัน", "ช่วยจัดทริป Tokyo 1 วันสำหรับคนมาครั้งแรก")
        ]

    items = [
        QuickReplyButton(action=MessageAction(label=label[:20], text=text[:300]))
        for label, text in buttons[:6]
    ]
    return QuickReply(items=items)
