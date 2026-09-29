"""
Recursive Document Chunker Module
ทำหน้าที่ตัดแบ่งเนื้อหาเอกสารออกเป็น Chunks ที่มีขนาดเหมาะสม
พร้อมเพิ่ม Metadata ละเอียด (Entity, Station, Category, Ward) สำหรับ Vector DB & Sparse BM25
"""
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.data_pipeline.cleaner import clean_text
from src.data_pipeline.models import DocumentChunkModel

class TokyoDocumentChunker:
    """
    คลาสสำหรับแบ่งเนื้อหาเอกสารท่องเที่ยวโตเกียว
    ใช้ Recursive Character Splitting โดยคำนึงถึงขอบเขตประโยคภาษาไทยและอังกฤษ
    """
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # ตัวตัดคำแยกตามลำดับความสำคัญ: ย่อหน้า -> ประโยค -> ช่องว่าง
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", " ", ""]
        )

    def chunk_place(self, place: Dict[str, Any]) -> List[DocumentChunkModel]:
        """
        นำข้อมูลสถานที่ 1 แห่งมาแบ่งเป็น chunks พร้อมแนบ metadata ครบถ้วน
        """
        chunks: List[DocumentChunkModel] = []
        place_id = place["place_id"]
        name_th = place["name_th"]
        name_en = place["name_en"]
        ward = place.get("ward", "")
        category = place.get("category", "")
        nearest_station = place.get("nearest_station_id", "")
        walk_min = place.get("walk_time_min", 0)

        # 1. Chunk ภาพรวมและประวัติ (Overview & History)
        desc_th = clean_text(place.get("description_th", ""))
        desc_en = clean_text(place.get("description_en", ""))

        text_splits_th = self.splitter.split_text(desc_th)
        text_splits_en = self.splitter.split_text(desc_en) if desc_en else [""] * len(text_splits_th)

        # หากจำนวน split ไม่เท่ากัน ขยายให้เท่ากัน
        max_splits = max(len(text_splits_th), len(text_splits_en))
        
        for idx in range(max_splits):
            c_th = text_splits_th[idx] if idx < len(text_splits_th) else ""
            c_en = text_splits_en[idx] if idx < len(text_splits_en) else ""
            
            chunk_id = f"C_{place_id}_{idx+1:02d}"
            title = f"{name_th} ({name_en}) - ส่วนที่ {idx+1}"
            
            # รวบรวม tags สำหรับช่วยในการค้นหา
            tags = [
                name_th,
                name_en,
                place.get("name_ja", ""),
                ward,
                category,
                nearest_station
            ]
            # กรองค่าว่าง
            tags = [t for t in tags if t]

            chunk_obj = DocumentChunkModel(
                chunk_id=chunk_id,
                place_id=place_id,
                title=title,
                content_th=c_th,
                content_en=c_en,
                ward=ward,
                category=category,
                nearest_station=nearest_station,
                walk_time_min=walk_min,
                tags=tags
            )
            chunks.append(chunk_obj)

        # 2. สร้าง Chunk พิเศษสำหรับการเดินทางและข้อมูลการเยี่ยมชม (Travel & Visiting Info)
        hours = place.get("opening_hours", "ไม่ระบุ")
        fee = place.get("admission_fee", "ฟรี")
        info_th = (
            f"ข้อมูลการเยี่ยมชมและการเดินทางสู่ {name_th} ({name_en}): "
            f"ตั้งอยู่ในเขต {ward} หมวดหมู่ {category} "
            f"สถานีรถไฟที่ใกล้ที่สุดคือ {nearest_station} โดยใช้เวลาเดินประมาณ {walk_min} นาที "
            f"เวลาเปิดทำการ: {hours} และอัตราค่าเข้าชม: {fee}"
        )
        info_en = (
            f"Visiting & Transit Guide for {name_en}: "
            f"Located in {ward} Ward, Category: {category}. "
            f"Nearest station is {nearest_station}, approximately {walk_min} minutes walk. "
            f"Opening hours: {hours}, Admission fee: {fee}."
        )
        
        info_chunk = DocumentChunkModel(
            chunk_id=f"C_{place_id}_INFO",
            place_id=place_id,
            title=f"{name_th} - ข้อมูลการเดินทางและการเยี่ยมชม",
            content_th=info_th,
            content_en=info_en,
            ward=ward,
            category=category,
            nearest_station=nearest_station,
            walk_time_min=walk_min,
            tags=[name_th, name_en, "การเดินทาง", "เวลาทำการ", "ค่าเข้าชม", nearest_station, ward]
        )
        chunks.append(info_chunk)

        return chunks
