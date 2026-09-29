# เอกสารสรุปแหล่งข้อมูลอ้างอิงสำหรับรายงาน (Data Sources & Citations)

เอกสารฉบับนี้รวบรวมรายการแหล่งข้อมูลปฐมภูมิ (Primary Data Sources) และทุติยภูมิ ที่ใช้ในการสร้าง Knowledge Base, Vector Database และ Knowledge Graph สำหรับโปรเจกต์ **Tokyo Smart Transit & Tourism Hybrid Graph RAG** เพื่อใช้แนบในรายงานการวิจัย (Project Report) ตามเกณฑ์ Rubric ด้าน **Data & Knowledge Base** และ **Documentation**

---

## 1. ตารางสรุปแหล่งข้อมูลหลัก (Primary Data Sources)

| แหล่งข้อมูล | องค์กร/ผู้ให้บริการ | รูปแบบข้อมูล (Format) | วัตถุประสงค์ในระบบ RAG | ลิงก์อ้างอิง (Official URL) |
| :--- | :--- | :--- | :--- | :--- |
| **JTA Sightseeing Database** | Japan Tourism Agency (JTA), กระทรวง MLIT ประเทศญี่ปุ่น | XLSX / Web Database | คำอธิบายสถานที่ท่องเที่ยวเชิงลึก, ประวัติศาสตร์, หมวดหมู่, และค่าเข้าชม สำหรับทำ **Dense Vector & Sparse BM25 Index** | [mlit.go.jp/tagengo-db/en](https://www.mlit.go.jp/tagengo-db/en/) |
| **駅データ.jp (EkiData JP)** | Station Database Japan | CSV / API | รหัสสถานีรถไฟ (Station Code), ชื่อสถานี 3 ภาษา (TH/EN/JA), พิกัด GPS (Lat/Lon) และสายรถไฟที่ผ่าน สำหรับสร้างโหนด **`(:Station)` ใน Neo4j** | [ekidata.jp](https://www.ekidata.jp/) |
| **OpenStreetMap (OSM) - Kanto Region** | Geofabrik / OSM Foundation | PBF / GeoJSON | พิกัดทางภูมิศาสตร์ของสถานที่ท่องเที่ยว (POIs) และคำนวณระยะทางเดินเท้า (Walking distance/duration) ไปยังสถานีที่ใกล้ที่สุด | [geofabrik.de/asia/japan/kanto.html](https://download.geofabrik.de/asia/japan/kanto.html) |
| **Tokyo Transit Route & Timetable Data** | Tokyo Metro & Bureau of Transportation (Toei) | Timetable Specifications | ระยะเวลาเดินทางจริงระหว่างสถานี (นาที) และโครงข่ายการเชื่อมต่อ เพื่อสร้าง Edge **`[:CONNECTED_TO]` สำหรับ Cypher Shortest Path** | [tokyometro.jp](https://www.tokyometro.jp/) / [kotsu.metro.tokyo.jp](https://www.kotsu.metro.tokyo.jp/) |

---

## 2. รายละเอียดการนำข้อมูลไปใช้งานตามสถาปัตยกรรม (Data Mapping)

### 2.1 ส่วนของ Knowledge Graph (Neo4j)
- **โหนดสถานที่ `(:Place)`:** สกัดจาก JTA Sightseeing Database และพิกัดจาก OpenStreetMap
- **โหนดสถานี `(:Station)` & สายรถไฟ `(:Line)`:** สกัดจาก 駅データ.jp และแผนผังระบบราง Tokyo Transit Network
- **เส้นเชื่อมโครงข่ายขนส่ง `[:CONNECTED_TO]`:** ใช้ระยะเวลาเดินทางจริงตามตารางเดินรถไฟของโตเกียว มี Property กำกับ:
  - `duration_min`: ระยะเวลาเดินทางระหว่างสถานี (นาที)
  - `distance_km`: ระยะทางจริง (กิโลเมตร)
  - `line_name`: ชื่อสายรถไฟ (เช่น JR Yamanote, Tokyo Metro Ginza Line)
- **เส้นเชื่อมสถานที่กับสถานี `[:NEAR_STATION]`:** คำนวณระยะเดินเท้าและทางออกที่สะดวกที่สุด (Exit Info)

### 2.2 ส่วนของ Dense & Hybrid RAG (Vector Database & BM25)
- **ข้อความคำอธิบาย (Descriptions):** ดึงเนื้อหาภาษาไทยและอังกฤษจาก JTA นำมาผ่านกระบวนการ Data Cleaning (แก้ปัญหาสระอำ/ช่องว่าง)
- **การตัด Chunk (Recursive Chunking):** แบ่งเนื้อหาเป็นก้อนละ 350 ตัวอักษร (Overlap 70 ตัวอักษร) พร้อมแนบ Rich Metadata:
  - `place_id`, `ward`, `category`, `nearest_station`, `walk_time_min`

---

## 3. สิทธิ์การใช้งานและการเผยแพร่ (Data License & Terms of Use)
- **JTA Sightseeing Database:** อนุญาตให้นำข้อความไปใช้ ดัดแปลง และเผยแพร่เพื่อการศึกษาและการวิจัย ภายใต้เงื่อนไขการระบุแหล่งที่มา (Attribution)
- **OpenStreetMap:** เผยแพร่ภายใต้สัญญาอนุญาต Open Data Commons Open Database License (ODbL)
- **駅データ.jp:** อนุญาตให้ใช้งานสำหรับการศึกษาและพัฒนาระบบตัวอย่าง
