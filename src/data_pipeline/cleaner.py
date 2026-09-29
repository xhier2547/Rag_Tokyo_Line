"""
Text Normalization & Cleaning Module
จัดการทำความสะอาดข้อความทั้งภาษาไทย ภาษาอังกฤษ และภาษาญี่ปุ่น
ขจัดอักขระแปลกปลอม สระลอย และช่องว่างซ้ำซ้อน
"""
import re

def clean_text(text: str) -> str:
    """
    ทำความสะอาดข้อความทั่วไป
    - แก้ปัญหาสระอำ/สระอาที่ encoding เพี้ยนจาก PDF/Web
    - ลบช่องว่างหรือแท็บซ้ำซ้อน
    - ตัดช่องว่างหัวท้าย
    """
    if not text:
        return ""
    
    # แก้ไขปัญหาการ encoding ผิดพลาดของสระอำในภาษาไทย
    text = text.replace('\ufffd\u0e32', 'ำ').replace(' \u0e33\ufffd', 'ำ').replace('\u0e33\ufffd', 'ำ')
    text = text.replace('\u0e33 \ufffd', 'ำ').replace('\ufffd', 'า').replace(' ำ', 'ำ')
    
    # ลบอักขระควบคุม (Control Characters) ที่ไม่ใช่ newline
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # ลบ space/tab ที่ซ้ำซ้อน
    text = re.sub(r'[ \t]+', ' ', text)
    
    # ลดบรรทัดว่างที่ซ้ำเกิน 2 บรรทัด
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def normalize_station_name(name: str) -> str:
    """
    จัดรูปแบบชื่อสถานีให้เป็นมาตรฐาน
    เช่น ตัดคำว่า Station, สถานี หรือ 駅 เพื่อใช้ในการจับคู่ (Entity Matching)
    """
    if not name:
        return ""
    cleaned = clean_text(name)
    cleaned = re.sub(r'(?i)\bstation\b', '', cleaned)
    cleaned = re.sub(r'^สถานี', '', cleaned)
    cleaned = re.sub(r'駅$', '', cleaned)
    return cleaned.strip()
