# แหล่งที่มาและการตรวจสอบย้อนกลับของชุดข้อมูล (Data Provenance & Lineage)
**โครงการ:** Tokyo Smart Transit & Tourism Hybrid Graph RAG  
**เวอร์ชันข้อมูล:** 2.0 (Expanded Production Dataset)  
**วันที่บันทึก:** กันยายน 2026  

---

## 1. วัตถุประสงค์ของเอกสาร (Data Provenance)
เอกสารนี้จัดทำขึ้นเพื่อแสดง **หลักฐานการตรวจสอบย้อนกลับ (Traceability & Lineage)** ของข้อมูลทั้งหมดที่ใช้ในการสร้างฐานความรู้เวกเตอร์ (Vector Store) และกราฟความรู้ (Knowledge Graph) ครอบคลุม **20 สถานีหลัก, 20 สถานที่ท่องเที่ยวแลนด์มาร์ก, 10 โรงแรมยอดนิยม และ 11 เส้นทางรถไฟ** เพื่อยืนยันว่าข้อมูลมิได้มาจากการสมมติขึ้นเอง แต่มาจากการรวบรวม ทำความสะอาด และสอบเทียบกับข้อมูลทางการของหน่วยงานขนส่งและส่งเสริมการท่องเที่ยวของประเทศญี่ปุ่น

---

## 2. แหล่งข้อมูลอ้างอิงทางการ (Authoritative Primary Sources)

| หมวดข้อมูล | แหล่งอ้างอิงปฐมภูมิ (Primary Source) | องค์กร/หน่วยงาน | ลิงก์อ้างอิงทางการ |
| :--- | :--- | :--- | :--- |
| **ข้อมูลโครงข่ายและเวลาเดินรถไฟ (Transit Network)** | Tokyo Metro Transit Map & Station Directory | Tokyo Metro Co., Ltd. (東京地下鉄株式会社) | [tokyometro.jp](https://www.tokyometro.jp/en/) |
| **ข้อมูลรถไฟสาย Toei & Yurikamome** | Toei Transportation & Yurikamome Transit Guide | Bureau of Transportation, Tokyo Metro Gov | [kotsu.metro.tokyo.jp](https://www.kotsu.metro.tokyo.jp/eng/) |
| **ข้อมูลรถไฟสาย JR Yamanote Line** | JR East Official Transit Network Guide | East Japan Railway Company (JR東日本) | [jreast.co.jp](https://www.jreast.co.jp/e/) |
| **ข้อมูลสถานที่ท่องเที่ยวและประวัติศาสตร์** | Japan National Tourism Organization (JNTO) | Japan Tourism Agency (JTA) | [japan.travel](https://www.japan.travel/en/) |
| **ข้อมูลวัฒนธรรมและพิพิธภัณฑ์โตเกียว** | Tokyo Convention & Visitors Bureau (TCVB) | GO TOKYO (Official Tokyo Travel Guide) | [gotokyo.org](https://www.gotokyo.org/en/) |
| **ข้อมูลที่พักและโรงแรม (Hotels & Accommodations)** | Japan Hotel Association & Official Hotel Registers | Japan Hotel Association (JHA) | [j-hotel.or.jp](https://www.j-hotel.or.jp/en/) |

---

## 3. รายละเอียดและสถิติชุดข้อมูล (Dataset Summary Statistics)

* **สถานีรถไฟ (Stations):** 20 สถานีหลักที่ครอบคลุมจุดเชื่อมต่อสำคัญทั่วมหานครโตเกียว
  * *รายชื่อสถานี:* Tokyo, Shinjuku, Shibuya, Asakusa, Ueno, Ginza, Akihabara, Harajuku, Roppongi, Oshiage, Tsukiji, Hamamatsucho, Shimbashi, Toyosu, Odaiba-Kaihinkoen, Korakuen, Shinjuku-gyoemmae, Omotesando, Shijo-mae, Daiba
* **สถานที่ท่องเที่ยว (Attractions & Landmarks):** 20 แห่ง ครอบคลุม 8 หมวดหมู่
  * *รายชื่อสถานที่:* Senso-ji, Tokyo Skytree, Shibuya Crossing, Meiji Jingu, Tokyo Tower, Shinjuku Gyoen, Akihabara Electric Town, Tsukiji Outer Market, Ueno Park, Roppongi Hills, GINZA SIX, Odaiba Unicorn Gundam, Imperial Palace, teamLab Planets, Ameyoko Market, Takeshita Street, Hamarikyu Gardens, Tokyo Dome City, Toyosu Market, Omotesando Hills
* **โรงแรมและที่พัก (Hotels):** 10 แห่ง แบ่งตามระดับงบประมาณ (Budget, Business/Mid-scale, Luxury)
  * *รายชื่อโรงแรม:* Hotel Gracery Shinjuku, The Tokyo Station Hotel, Shibuya Stream Excel Hotel Tokyu, Asakusa View Hotel, Dormy Inn Akihabara Hot Springs, Mitsui Garden Hotel Ginza Premier, Grand Nikko Tokyo Daiba, Hotel New Otani Tokyo, APA Hotel Roppongi Six, OMO5 Tokyo Otsuka by Hoshino Resorts
* **เส้นทางรถไฟ (Transit Lines):** 11 เส้นทาง
  * *รายชื่อสายรถไฟ:* JR Yamanote, Tokyo Metro Ginza, Tokyo Metro Marunouchi, Tokyo Metro Hibiya, Tokyo Metro Tozai, Tokyo Metro Chiyoda, Tokyo Metro Yurakucho, Tokyo Metro Hanzomon, Tokyo Metro Namboku, Toei Asakusa, Toei Oedo, Yurikamome Line
* **เส้นเชื่อมโยงในกราฟ (Knowledge Graph Edges):** 68 เส้นเชื่อมความสัมพันธ์ (CONNECTED_TO, LOCATED_NEAR, CONNECTED_TO_STATION)

---

## 4. กระบวนการประมวลผลข้อมูล (Data Preprocessing & Chunking Pipeline)
1. **Data Normalization:** ทำความสะอาดชื่อสถานีภาษาไทย ภาษาอังกฤษ และภาษาญี่ปุ่น ให้เป็นมาตรฐานเดียวกัน
2. **Metadata Tagging:** ระบุ `nearest_station_id`, `walk_time_min`, `ward`, `category`, `admission_fee`, `opening_hours` ลงในทุก Chunk
3. **Structured Chunking:** แบ่งเนื้อหาเป็นส่วนภาพรวม (Overview), การเดินทาง (Transit), และประวัติ/ไฮไลท์ (Highlights) เพื่อให้ Vector Retrieval สามารถคัดแยกเนื้อหาได้ตรงจุด
4. **Graph Construction:** สร้าง Graph Schema 3 Node Types (`Station`, `Place`, `Hotel`) และ 3 Relationship Types พร้อมเก็บระยะเวลาและระยะทางบน Edge จริง
