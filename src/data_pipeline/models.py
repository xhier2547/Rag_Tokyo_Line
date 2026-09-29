"""
Pydantic Data Models สำหรับตรวจสอบความถูกต้องของข้อมูล (Schema Validation)
ครอบคลุม Places, Stations, Lines, Graph Edges และ Document Chunks
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class PlaceModel(BaseModel):
    place_id: str = Field(..., description="รหัสสถานที่ เช่น P_SENSOJI")
    name_th: str = Field(..., description="ชื่อสถานที่ภาษาไทย")
    name_en: str = Field(..., description="ชื่อสถานที่ภาษาอังกฤษ")
    name_ja: str = Field(..., description="ชื่อสถานที่ภาษาญี่ปุ่น")
    ward: str = Field(..., description="เขตในโตเกียว เช่น Taito, Shibuya")
    category: str = Field(..., description="หมวดหมู่สถานที่")
    latitude: float = Field(..., ge=35.0, le=36.0, description="พิกัดละติจูดในโตเกียว")
    longitude: float = Field(..., ge=139.0, le=140.5, description="พิกัดลองจิจูดในโตเกียว")
    description_th: str = Field(..., description="คำอธิบายภาษาไทยเชิงลึก")
    description_en: str = Field(..., description="คำอธิบายภาษาอังกฤษ")
    opening_hours: str = Field(..., description="เวลาทำการ")
    admission_fee: str = Field(..., description="ค่าเข้าชม")
    nearest_station_id: str = Field(..., description="รหัสสถานีที่ใกล้ที่สุด")
    walk_time_min: int = Field(..., ge=0, description="เวลาเดินจากสถานี (นาที)")

class StationModel(BaseModel):
    station_id: str = Field(..., description="รหัสสถานี เช่น ST_SHINJUKU")
    name_th: str = Field(..., description="ชื่อสถานีภาษาไทย")
    name_en: str = Field(..., description="ชื่อสถานีภาษาอังกฤษ")
    name_ja: str = Field(..., description="ชื่อสถานีภาษาญี่ปุ่น")
    lines: str = Field(..., description="รหัสสายรถไฟที่ผ่าน คั่นด้วยเซมิโคลอน")
    ward: str = Field(..., description="เขตที่ตั้งของสถานี")
    latitude: float = Field(..., description="พิกัดละติจูด")
    longitude: float = Field(..., description="พิกัดลองจิจูด")

class LineModel(BaseModel):
    line_id: str = Field(..., description="รหัสสายรถไฟ เช่น LN_YAMANOTE")
    name_th: str = Field(..., description="ชื่อสายภาษาไทย")
    name_en: str = Field(..., description="ชื่อสายภาษาอังกฤษ")
    line_code: str = Field(..., description="ตัวย่อสาย เช่น JY, G, M")
    operator: str = Field(..., description="ผู้ให้บริการ เช่น JR East, Tokyo Metro")
    color: str = Field(..., description="รหัสสีประจำสาย เช่น #9ACD32")

class TransitEdgeModel(BaseModel):
    from_station_id: str = Field(..., description="รหัสสถานีต้นทาง")
    to_station_id: str = Field(..., description="รหัสสถานีปลายทาง")
    line_id: str = Field(..., description="รหัสสายรถไฟที่เชื่อมต่อ")
    line_name: str = Field(..., description="ชื่อสายรถไฟ")
    duration_min: int = Field(..., ge=1, description="ระยะเวลาเดินทางระหว่างสถานี (นาที)")
    distance_km: float = Field(..., ge=0.1, description="ระยะทางระหว่างสถานี (กม.)")

class PlaceStationEdgeModel(BaseModel):
    place_id: str = Field(..., description="รหัสสถานที่")
    station_id: str = Field(..., description="รหัสสถานี")
    walk_time_min: int = Field(..., ge=0, description="เวลาเดิน (นาที)")
    distance_m: int = Field(..., ge=0, description="ระยะทางเดิน (เมตร)")
    exit_info: str = Field(..., description="ทางออกสถานีที่สะดวกที่สุด")

class DocumentChunkModel(BaseModel):
    chunk_id: str = Field(..., description="รหัส chunk เอกสาร เช่น C_SENSOJI_01")
    place_id: str = Field(..., description="รหัสสถานที่อ้างอิง")
    title: str = Field(..., description="หัวข้อของ chunk")
    content_th: str = Field(..., description="เนื้อหาภาษาไทย")
    content_en: str = Field(..., description="เนื้อหาภาษาอังกฤษ")
    ward: str = Field(..., description="เขตในโตเกียว")
    category: str = Field(..., description="หมวดหมู่")
    nearest_station: str = Field(..., description="สถานีใกล้เคียง")
    walk_time_min: int = Field(..., description="เวลาเดิน (นาที)")
    tags: List[str] = Field(default_factory=list, description="แท็กสำหรับค้นหา")
