"""
Curated Tokyo Tourism & Transit Dataset
รวบรวมข้อมูลสถานที่ท่องเที่ยว สถานีรถไฟ สายรถไฟ และโครงข่ายการเดินทางในโตเกียว
อ้างอิงจาก JTA Sightseeing Database, 駅データ.jp และ OpenStreetMap
"""

LINES_DATA = [
    {
        "line_id": "LN_YAMANOTE",
        "name_th": "รถไฟสายยามาโนเตะ (JR Yamanote Line)",
        "name_en": "JR Yamanote Line",
        "line_code": "JY",
        "operator": "JR East",
        "color": "#9ACD32"  # Yellow-Green
    },
    {
        "line_id": "LN_GINZA",
        "name_th": "รถไฟใต้ดินสายกินซ่า (Tokyo Metro Ginza Line)",
        "name_en": "Tokyo Metro Ginza Line",
        "line_code": "G",
        "operator": "Tokyo Metro",
        "color": "#FF9500"  # Orange
    },
    {
        "line_id": "LN_MARUNOUCHI",
        "name_th": "รถไฟใต้ดินสายมารุโนอุจิ (Tokyo Metro Marunouchi Line)",
        "name_en": "Tokyo Metro Marunouchi Line",
        "line_code": "M",
        "operator": "Tokyo Metro",
        "color": "#E60012"  # Red
    },
    {
        "line_id": "LN_HIBIYA",
        "name_th": "รถไฟใต้ดินสายฮิบิยะ (Tokyo Metro Hibiya Line)",
        "name_en": "Tokyo Metro Hibiya Line",
        "line_code": "H",
        "operator": "Tokyo Metro",
        "color": "#B5B5AC"  # Silver
    },
    {
        "line_id": "LN_HANZOMON",
        "name_th": "รถไฟใต้ดินสายฮันโซมอน (Tokyo Metro Hanzomon Line)",
        "name_en": "Tokyo Metro Hanzomon Line",
        "line_code": "Z",
        "operator": "Tokyo Metro",
        "color": "#8F76D6"  # Purple
    },
    {
        "line_id": "LN_ASAKUSA",
        "name_th": "รถไฟใต้ดินสายอาซากุสะ (Toei Asakusa Line)",
        "name_en": "Toei Asakusa Line",
        "line_code": "A",
        "operator": "Toei Subway",
        "color": "#E85298"  # Rose
    },
    {
        "line_id": "LN_OEDO",
        "name_th": "รถไฟใต้ดินสายโอเอโดะ (Toei Oedo Line)",
        "name_en": "Toei Oedo Line",
        "line_code": "E",
        "operator": "Toei Subway",
        "color": "#B6007A"  # Magenta
    },
    {
        "line_id": "LN_CHUO_SOBU",
        "name_th": "รถไฟสายชูโอ-โซบุ (JR Chuo-Sobu Line)",
        "name_en": "JR Chuo-Sobu Line",
        "line_code": "JB",
        "operator": "JR East",
        "color": "#FFD700"  # Yellow
    },
    {
        "line_id": "LN_YURIKAMOME",
        "name_th": "รถไฟโมโนเรลสายยูริคาโมเมะ (Yurikamome Line)",
        "name_en": "Yurikamome Line",
        "line_code": "U",
        "operator": "Tokyo Waterfront New Transit",
        "color": "#0099FF"  # Blue
    }
]

STATIONS_DATA = [
    {
        "station_id": "ST_TOKYO",
        "name_th": "สถานีโตเกียว",
        "name_en": "Tokyo Station",
        "name_ja": "東京駅",
        "lines": "LN_YAMANOTE;LN_MARUNOUCHI",
        "ward": "Chiyoda",
        "latitude": 35.681236,
        "longitude": 139.767125
    },
    {
        "station_id": "ST_SHINJUKU",
        "name_th": "สถานีชินจูกุ",
        "name_en": "Shinjuku Station",
        "name_ja": "新宿駅",
        "lines": "LN_YAMANOTE;LN_MARUNOUCHI;LN_OEDO;LN_CHUO_SOBU",
        "ward": "Shinjuku",
        "latitude": 35.689607,
        "longitude": 139.700571
    },
    {
        "station_id": "ST_SHIBUYA",
        "name_th": "สถานีชิบูย่า",
        "name_en": "Shibuya Station",
        "name_ja": "渋谷駅",
        "lines": "LN_YAMANOTE;LN_GINZA;LN_HANZOMON",
        "ward": "Shibuya",
        "latitude": 35.658034,
        "longitude": 139.701636
    },
    {
        "station_id": "ST_ASAKUSA",
        "name_th": "สถานีอาซากุสะ",
        "name_en": "Asakusa Station",
        "name_ja": "浅草駅",
        "lines": "LN_GINZA;LN_ASAKUSA",
        "ward": "Taito",
        "latitude": 35.712285,
        "longitude": 139.798363
    },
    {
        "station_id": "ST_UENO",
        "name_th": "สถานีอุเอโนะ",
        "name_en": "Ueno Station",
        "name_ja": "上野駅",
        "lines": "LN_YAMANOTE;LN_GINZA;LN_HIBIYA",
        "ward": "Taito",
        "latitude": 35.713768,
        "longitude": 139.777254
    },
    {
        "station_id": "ST_AKIHABARA",
        "name_th": "สถานีอากิฮาบาระ",
        "name_en": "Akihabara Station",
        "name_ja": "秋葉原駅",
        "lines": "LN_YAMANOTE;LN_HIBIYA;LN_CHUO_SOBU",
        "ward": "Chiyoda",
        "latitude": 35.698383,
        "longitude": 139.773072
    },
    {
        "station_id": "ST_GINZA",
        "name_th": "สถานีกินซ่า",
        "name_en": "Ginza Station",
        "name_ja": "銀座駅",
        "lines": "LN_GINZA;LN_MARUNOUCHI;LN_HIBIYA",
        "ward": "Chuo",
        "latitude": 35.671989,
        "longitude": 139.763965
    },
    {
        "station_id": "ST_ROPPONGI",
        "name_th": "สถานีรปปงงิ",
        "name_en": "Roppongi Station",
        "name_ja": "六本木駅",
        "lines": "LN_HIBIYA;LN_OEDO",
        "ward": "Minato",
        "latitude": 35.662837,
        "longitude": 139.731443
    },
    {
        "station_id": "ST_OSHIAGE",
        "name_th": "สถานีโอชิอาเกะ (สกายทรี)",
        "name_en": "Oshiage (Skytree) Station",
        "name_ja": "押上駅",
        "lines": "LN_ASAKUSA;LN_HANZOMON",
        "ward": "Sumida",
        "latitude": 35.710609,
        "longitude": 139.813292
    },
    {
        "station_id": "ST_HARAJUKU",
        "name_th": "สถานีฮาราจูกุ",
        "name_en": "Harajuku Station",
        "name_ja": "原宿駅",
        "lines": "LN_YAMANOTE",
        "ward": "Shibuya",
        "latitude": 35.670168,
        "longitude": 139.702687
    },
    {
        "station_id": "ST_SHIMBASHI",
        "name_th": "สถานีชิมบาชิ",
        "name_en": "Shimbashi Station",
        "name_ja": "新橋駅",
        "lines": "LN_YAMANOTE;LN_GINZA;LN_ASAKUSA;LN_YURIKAMOME",
        "ward": "Minato",
        "latitude": 35.666379,
        "longitude": 139.758340
    },
    {
        "station_id": "ST_HAMAMATSUCHO",
        "name_th": "สถานีฮามามัตสึโจ (โตเกียวทาวเวอร์)",
        "name_en": "Hamamatsucho Station",
        "name_ja": "浜松町駅",
        "lines": "LN_YAMANOTE;LN_OEDO",
        "ward": "Minato",
        "latitude": 35.655381,
        "longitude": 139.757135
    },
    {
        "station_id": "ST_IKEBUKURO",
        "name_th": "สถานีอิเคะบุคุโระ",
        "name_en": "Ikebukuro Station",
        "name_ja": "池袋駅",
        "lines": "LN_YAMANOTE;LN_MARUNOUCHI",
        "ward": "Toshima",
        "latitude": 35.729503,
        "longitude": 139.710900
    },
    {
        "station_id": "ST_ODAIBA_KAIHINKOEN",
        "name_th": "สถานีโอไดบะ ไคฮินโคเอ็น",
        "name_en": "Odaiba-Kaihinkoen Station",
        "name_ja": "お台場海浜公園駅",
        "lines": "LN_YURIKAMOME",
        "ward": "Minato",
        "latitude": 35.629344,
        "longitude": 139.777085
    },
    {
        "station_id": "ST_SHINJUKU_GYOEMMAE",
        "name_th": "สถานีชินจูกุเกียวเอ็นมาเอะ",
        "name_en": "Shinjuku-gyoemmae Station",
        "name_ja": "新宿御苑前駅",
        "lines": "LN_MARUNOUCHI",
        "ward": "Shinjuku",
        "latitude": 35.688647,
        "longitude": 139.710928
    },
    {
        "station_id": "ST_TSUKIJI",
        "name_th": "สถานีสึกิจิ",
        "name_en": "Tsukiji Station",
        "name_ja": "築地駅",
        "lines": "LN_HIBIYA",
        "ward": "Chuo",
        "latitude": 35.667794,
        "longitude": 139.772591
    },
    {
        "station_id": "ST_TOYOSU",
        "name_th": "สถานีโทโยสุ",
        "name_en": "Toyosu Station",
        "name_ja": "豊洲駅",
        "lines": "LN_YURIKAMOME",
        "ward": "Koto",
        "latitude": 35.654824,
        "longitude": 139.796338
    }
]

# โครงข่ายเชื่อมต่อระหว่างสถานีรถไฟ (Transit Edges)
# กำหนดระยะเวลา (นาที) และระยะทาง (กม.) ตามเวลาเดินรถจริง
TRANSIT_EDGES_DATA = [
    # 1. JR Yamanote Line (สถานีหลัก)
    {"from_station_id": "ST_TOKYO", "to_station_id": "ST_SHIMBASHI", "line_id": "LN_YAMANOTE", "line_name": "JR Yamanote Line", "duration_min": 4, "distance_km": 1.9},
    {"from_station_id": "ST_SHIMBASHI", "to_station_id": "ST_HAMAMATSUCHO", "line_id": "LN_YAMANOTE", "line_name": "JR Yamanote Line", "duration_min": 2, "distance_km": 1.2},
    {"from_station_id": "ST_HAMAMATSUCHO", "to_station_id": "ST_SHIBUYA", "line_id": "LN_YAMANOTE", "line_name": "JR Yamanote Line", "duration_min": 14, "distance_km": 7.4},
    {"from_station_id": "ST_SHIBUYA", "to_station_id": "ST_HARAJUKU", "line_id": "LN_YAMANOTE", "line_name": "JR Yamanote Line", "duration_min": 2, "distance_km": 1.2},
    {"from_station_id": "ST_HARAJUKU", "to_station_id": "ST_SHINJUKU", "line_id": "LN_YAMANOTE", "line_name": "JR Yamanote Line", "duration_min": 4, "distance_km": 2.4},
    {"from_station_id": "ST_SHINJUKU", "to_station_id": "ST_IKEBUKURO", "line_id": "LN_YAMANOTE", "line_name": "JR Yamanote Line", "duration_min": 9, "distance_km": 4.8},
    {"from_station_id": "ST_IKEBUKURO", "to_station_id": "ST_UENO", "line_id": "LN_YAMANOTE", "line_name": "JR Yamanote Line", "duration_min": 16, "distance_km": 8.1},
    {"from_station_id": "ST_UENO", "to_station_id": "ST_AKIHABARA", "line_id": "LN_YAMANOTE", "line_name": "JR Yamanote Line", "duration_min": 3, "distance_km": 1.6},
    {"from_station_id": "ST_AKIHABARA", "to_station_id": "ST_TOKYO", "line_id": "LN_YAMANOTE", "line_name": "JR Yamanote Line", "duration_min": 4, "distance_km": 2.0},

    # 2. Tokyo Metro Ginza Line
    {"from_station_id": "ST_SHIBUYA", "to_station_id": "ST_GINZA", "line_id": "LN_GINZA", "line_name": "Tokyo Metro Ginza Line", "duration_min": 16, "distance_km": 6.7},
    {"from_station_id": "ST_GINZA", "to_station_id": "ST_SHIMBASHI", "line_id": "LN_GINZA", "line_name": "Tokyo Metro Ginza Line", "duration_min": 2, "distance_km": 0.9},
    {"from_station_id": "ST_GINZA", "to_station_id": "ST_UENO", "line_id": "LN_GINZA", "line_name": "Tokyo Metro Ginza Line", "duration_min": 12, "distance_km": 4.5},
    {"from_station_id": "ST_UENO", "to_station_id": "ST_ASAKUSA", "line_id": "LN_GINZA", "line_name": "Tokyo Metro Ginza Line", "duration_min": 5, "distance_km": 2.2},

    # 3. Tokyo Metro Marunouchi Line
    {"from_station_id": "ST_IKEBUKURO", "to_station_id": "ST_TOKYO", "line_id": "LN_MARUNOUCHI", "line_name": "Tokyo Metro Marunouchi Line", "duration_min": 17, "distance_km": 8.7},
    {"from_station_id": "ST_TOKYO", "to_station_id": "ST_GINZA", "line_id": "LN_MARUNOUCHI", "line_name": "Tokyo Metro Marunouchi Line", "duration_min": 3, "distance_km": 1.1},
    {"from_station_id": "ST_GINZA", "to_station_id": "ST_SHINJUKU_GYOEMMAE", "line_id": "LN_MARUNOUCHI", "line_name": "Tokyo Metro Marunouchi Line", "duration_min": 13, "distance_km": 5.9},
    {"from_station_id": "ST_SHINJUKU_GYOEMMAE", "to_station_id": "ST_SHINJUKU", "line_id": "LN_MARUNOUCHI", "line_name": "Tokyo Metro Marunouchi Line", "duration_min": 3, "distance_km": 1.1},

    # 4. Tokyo Metro Hibiya Line
    {"from_station_id": "ST_UENO", "to_station_id": "ST_AKIHABARA", "line_id": "LN_HIBIYA", "line_name": "Tokyo Metro Hibiya Line", "duration_min": 3, "distance_km": 1.6},
    {"from_station_id": "ST_AKIHABARA", "to_station_id": "ST_GINZA", "line_id": "LN_HIBIYA", "line_name": "Tokyo Metro Hibiya Line", "duration_min": 9, "distance_km": 3.7},
    {"from_station_id": "ST_GINZA", "to_station_id": "ST_TSUKIJI", "line_id": "LN_HIBIYA", "line_name": "Tokyo Metro Hibiya Line", "duration_min": 3, "distance_km": 1.4},
    {"from_station_id": "ST_GINZA", "to_station_id": "ST_ROPPONGI", "line_id": "LN_HIBIYA", "line_name": "Tokyo Metro Hibiya Line", "duration_min": 9, "distance_km": 4.1},

    # 5. Toei Asakusa Line & Hanzomon Line (เชื่อมสู่ Oshiage / Skytree)
    {"from_station_id": "ST_ASAKUSA", "to_station_id": "ST_OSHIAGE", "line_id": "LN_ASAKUSA", "line_name": "Toei Asakusa Line", "duration_min": 3, "distance_km": 1.5},
    {"from_station_id": "ST_SHIMBASHI", "to_station_id": "ST_ASAKUSA", "line_id": "LN_ASAKUSA", "line_name": "Toei Asakusa Line", "duration_min": 14, "distance_km": 6.8},
    {"from_station_id": "ST_SHIBUYA", "to_station_id": "ST_OSHIAGE", "line_id": "LN_HANZOMON", "line_name": "Tokyo Metro Hanzomon Line", "duration_min": 31, "distance_km": 15.2},

    # 6. Toei Oedo Line (เชื่อม Roppongi, Shinjuku, Hamamatsucho)
    {"from_station_id": "ST_SHINJUKU", "to_station_id": "ST_ROPPONGI", "line_id": "LN_OEDO", "line_name": "Toei Oedo Line", "duration_min": 9, "distance_km": 4.5},
    {"from_station_id": "ST_ROPPONGI", "to_station_id": "ST_HAMAMATSUCHO", "line_id": "LN_OEDO", "line_name": "Toei Oedo Line", "duration_min": 6, "distance_km": 2.8},

    # 7. Yurikamome Line (ไป Odaiba & Toyosu)
    {"from_station_id": "ST_SHIMBASHI", "to_station_id": "ST_ODAIBA_KAIHINKOEN", "line_id": "LN_YURIKAMOME", "line_name": "Yurikamome Line", "duration_min": 13, "distance_km": 5.0},
    {"from_station_id": "ST_ODAIBA_KAIHINKOEN", "to_station_id": "ST_TOYOSU", "line_id": "LN_YURIKAMOME", "line_name": "Yurikamome Line", "duration_min": 16, "distance_km": 6.9}
]

# ข้อมูลสถานที่ท่องเที่ยว (Places Data) พร้อมเนื้อหาเชิงลึก
PLACES_DATA = [
    {
        "place_id": "P_SENSOJI",
        "name_th": "วัดเซ็นโซจิ (วัดอาซากุสะ)",
        "name_en": "Senso-ji Temple",
        "name_ja": "浅草寺",
        "ward": "Taito",
        "category": "Temple & Shrine",
        "latitude": 35.714765,
        "longitude": 139.796655,
        "description_th": "วัดเซ็นโซจิเป็นวัดพุทธที่เก่าแก่ที่สุดในกรุงโตเกียว สร้างขึ้นในปี ค.ศ. 628 มีเอกลักษณ์คือประตูคามินาริโมง (Kaminarimon) ที่แขวนโคมแดงยักษ์อันเลื่องชื่อ ภายในมีถนนคนเดินนากามิเสะ (Nakamise-dori) ทอดยาวกว่า 250 เมตร เต็มไปด้วยร้านขายขนมพื้นเมือง เช่น ขนมเซมเบ้ มันจูทอด และของที่ระลึกดั้งเดิม เป็นจุดหมายยอดนิยมที่ผู้คนมาสักการะองค์เจ้าแม่กวนอิมเพื่อขอพรเรื่องความสุขและความสำเร็จ",
        "description_en": "Senso-ji is Tokyo's oldest and most significant Buddhist temple, founded in 628 AD. Famous for its colossal red paper lantern at the Kaminarimon (Thunder Gate) and the vibrant Nakamise shopping street offering traditional snacks and souvenirs.",
        "opening_hours": "06:00 - 17:00 (ตัวโบสถ์หลัก) / บริเวณวัดเปิด 24 ชั่วโมง",
        "admission_fee": "เข้าชมฟรี",
        "nearest_station_id": "ST_ASAKUSA",
        "walk_time_min": 5
    },
    {
        "place_id": "P_TOKYO_SKYTREE",
        "name_th": "โตเกียวสกายทรี",
        "name_en": "Tokyo Skytree",
        "name_ja": "東京スカイツリー",
        "ward": "Sumida",
        "category": "Landmark & Viewpoint",
        "latitude": 35.710063,
        "longitude": 139.810700,
        "description_th": "โตเกียวสกายทรีเป็นหอคอยกระจายเสียงที่สูงที่สุดในโลก ด้วยความสูง 634 เมตร ด้านบนมีจุดชมวิว 2 ชั้น ได้แก่ Tembo Deck (ความสูง 350 เมตร) และ Tembo Galleria (ความสูง 450 เมตร) ที่สามารถมองเห็นทิวทัศน์ของมหานครโตเกียวแบบ 360 องศา และในวันที่ฟ้าโปร่งสามารถมองเห็นภูเขาไฟฟูจิได้อย่างชัดเจน ที่ฐานหอคอยมีศูนย์การค้า Tokyo Solamachi และพิพิธภัณฑ์สัตว์น้ำ Sumida Aquarium",
        "description_en": "Tokyo Skytree is the world's tallest freestanding broadcast tower at 634 meters. Features two observation decks offering panoramic 360-degree views of Tokyo and Mount Fuji on clear days, with the large Solamachi shopping complex at its base.",
        "opening_hours": "10:00 - 21:00 (รอบสุดท้าย 20:00)",
        "admission_fee": "ผู้ใหญ่เริ่มต้น 2,100 เยน (ขึ้นอยู่กับชั้นชมวิว)",
        "nearest_station_id": "ST_OSHIAGE",
        "walk_time_min": 2
    },
    {
        "place_id": "P_SHIBUYA_CROSSING",
        "name_th": "ห้าแยกชิบูย่าและรูปปั้นฮาจิโกะ",
        "name_en": "Shibuya Crossing & Hachiko Statue",
        "name_ja": "渋谷スクランブル交差点",
        "ward": "Shibuya",
        "category": "Landmark & Viewpoint",
        "latitude": 35.659482,
        "longitude": 139.700553,
        "description_th": "ห้าแยกชิบูย่าเป็นทางข้ามถนนที่มีผู้คนสัญจรพลุกพล่านที่สุดในโลก โดยมีคนเดินข้ามมากถึง 3,000 คนต่อหนึ่งสัญญาณไฟเขียว รายล้อมด้วยป้ายโฆษณาจอยักษ์แสงสีนีออน ใกล้กันมีรูปปั้นสุนัขยอดกตัญญู 'ฮาจิโกะ' ซึ่งเป็นจุดนัดพบยอดนิยมของชาวโตเกียว นักท่องเที่ยวสามารถชมวิวมุมสูงของห้าแยกได้จาก Shibuya Sky หรือร้านกาแฟชื่อดังรอบแยก",
        "description_en": "The world's busiest pedestrian crossing, accommodating up to 3,000 people per green light. Surrounded by neon screens and adjacent to the iconic bronze statue of loyal dog Hachiko outside Shibuya Station.",
        "opening_hours": "เปิด 24 ชั่วโมง",
        "admission_fee": "เข้าชมฟรี",
        "nearest_station_id": "ST_SHIBUYA",
        "walk_time_min": 1
    },
    {
        "place_id": "P_MEIJI_JINGU",
        "name_th": "ศาลเจ้าเมจิ",
        "name_en": "Meiji Jingu Shrine",
        "name_ja": "明治神宮",
        "ward": "Shibuya",
        "category": "Temple & Shrine",
        "latitude": 35.676398,
        "longitude": 139.699326,
        "description_th": "ศาลเจ้าชินโตที่สร้างขึ้นเพื่ออุทิศถวายแด่จักรพรรดิเมจิและจักรพรรดินีโชเก็ง ตั้งอยู่ท่ามกลางผืนป่าธรรมชาติอันเงียบสงบกว่า 100,000 ต้นใจกลางโตเกียว ทางเข้ามีเสาโทริอิไม้ขนาดใหญ่ ซุ้มถังสาเกบูชา และเส้นทางเดินกรวดอันร่มรื่น เป็นสถานที่ศักดิ์สิทธิ์ที่นิยมจัดพิธีแต่งงานแบบชินโตดั้งเดิมและขอพรปีใหม่ (Hatsumode)",
        "description_en": "A tranquil Shinto shrine dedicated to Emperor Meiji and Empress Shoken, nestled within a lush 170-acre evergreen forest in the heart of Tokyo. Known for its massive wooden torii gates and vibrant sake barrel displays.",
        "opening_hours": "เปิดตั้งแต่พระอาทิตย์ขึ้นจนถึงพระอาทิตย์ตก (ประมาณ 05:00 - 18:00)",
        "admission_fee": "เข้าชมฟรี (ส่วนสวนชั้นใน Inner Garden มีค่าเข้า 500 เยน)",
        "nearest_station_id": "ST_HARAJUKU",
        "walk_time_min": 3
    },
    {
        "place_id": "P_TOKYO_TOWER",
        "name_th": "โตเกียวทาวเวอร์",
        "name_en": "Tokyo Tower",
        "name_ja": "東京タワー",
        "ward": "Minato",
        "category": "Landmark & Viewpoint",
        "latitude": 35.658580,
        "longitude": 139.745433,
        "description_th": "หอคอยสื่อสารโครงเหล็กสีส้มขาวอันเป็นสัญลักษณ์คลาสสิกของโตเกียว สร้างขึ้นในปี ค.ศ. 1958 ด้วยความสูง 333 เมตร ได้รับแรงบันดาลใจจากหอไอเฟลในปารีส มีจุดชมวิว Main Deck (150 เมตร) และ Top Deck (250 เมตร) ในยามค่ำคืนจะมีการเปิดไฟประดับสวยงาม (Light-up) เปลี่ยนตามฤดูกาลและเทศกาล",
        "description_en": "Built in 1958, this 333-meter retro-chic communications tower was modeled after Paris's Eiffel Tower. Features observation decks at 150m and 250m, glowing with spectacular seasonal illuminations at night.",
        "opening_hours": "09:00 - 22:30",
        "admission_fee": "Main Deck ผู้ใหญ่ 1,200 เยน / Top Deck Tour 3,000 เยน",
        "nearest_station_id": "ST_HAMAMATSUCHO",
        "walk_time_min": 15
    },
    {
        "place_id": "P_SHINJUKU_GYOEN",
        "name_th": "สวนสาธารณะชินจูกุเกียวเอ็น",
        "name_en": "Shinjuku Gyoen National Garden",
        "name_ja": "新宿御苑",
        "ward": "Shinjuku",
        "category": "Nature & Park",
        "latitude": 35.685176,
        "longitude": 139.710052,
        "description_th": "สวนสาธารณะขนาดใหญ่เนื้อที่กว่า 144 เอเคอร์ ผสมผสานศิลปะการจัดสวน 3 รูปแบบไว้ด้วยกันอย่างลงตัว ได้แก่ สวนสไตล์ญี่ปุ่นดั้งเดิม สวนสมมาตรสไตล์ฝรั่งเศส และสวนภูมิทัศน์สไตล์อังกฤษ ในช่วงฤดูใบไม้ผลิเป็นจุดชมซากุระยอดนิยมที่มีต้นซากุระกว่าพันต้นหลากสายพันธุ์ และในฤดูใบไม้ร่วงใบไม้จะเปลี่ยนเป็นสีแดงสดใส",
        "description_en": "One of Tokyo's largest and most popular national parks, blending three distinct landscape styles: Japanese traditional, English landscape, and French formal. A premier cherry blossom viewing haven in spring.",
        "opening_hours": "09:00 - 16:30 (ปิดทุกวันจันทร์)",
        "admission_fee": "ผู้ใหญ่ 500 เยน",
        "nearest_station_id": "ST_SHINJUKU_GYOEMMAE",
        "walk_time_min": 5
    },
    {
        "place_id": "P_AKIHABARA_ELECTRIC",
        "name_th": "ย่านเครื่องใช้ไฟฟ้าและอนิเมะอากิฮาบาระ",
        "name_en": "Akihabara Electric Town",
        "name_ja": "秋葉原電気街",
        "ward": "Chiyoda",
        "category": "Shopping & Entertainment",
        "latitude": 35.699732,
        "longitude": 139.771380,
        "description_th": "ศูนย์กลางวัฒนธรรมโอตาคุ อนิเมะ มังงะ ฟิกเกอร์ และอุปกรณ์อิเล็กทรอนิกส์ระดับโลก บนถนน Chuo-dori เต็มไปด้วยร้านค้าชื่อดัง เช่น Mandarake, Radio Kaikan, Yodobashi Camera รวมถึงคาเฟ่ธีมเมดคาเฟ่ (Maid Cafe) และตู้เกมอาร์เคดหลายชั้น",
        "description_en": "The global Mecca for otaku pop culture, gaming, anime, manga, retro electronics, and multi-story hobby shops like Mandarake, Radio Kaikan, and maid cafes.",
        "opening_hours": "ร้านค้าส่วนใหญ่เปิด 10:00 - 20:00",
        "admission_fee": "เดินชมฟรี",
        "nearest_station_id": "ST_AKIHABARA",
        "walk_time_min": 1
    },
    {
        "place_id": "P_TSUKIJI_OUTER",
        "name_th": "ตลาดปลาสึกิจิ (ตลาดนอก)",
        "name_en": "Tsukiji Outer Market",
        "name_ja": "築地場外市場",
        "ward": "Chuo",
        "category": "Food & Market",
        "latitude": 35.665518,
        "longitude": 139.770743,
        "description_th": "ตลาดอาหารสตรีทฟู้ดและวัตถุดิบทางทะเลสดใหม่ใจกลางโตเกียว มีร้านค้าและแผงลอยกว่า 400 ร้าน จำหน่ายซาชิมิสด ข้าวหน้าปลาดิบ (Kaisendon) หอยเชลล์ย่าง ไข่หวานย่างร้อนๆ (Tamagoyaki) และผลไม้ตามฤดูกาล เป็นสวรรค์ของนักชิมที่เปิดให้บริการตั้งแต่เช้าตรู่",
        "description_en": "A lively open-air seafood and food haven with hundreds of stalls offering fresh sashimi, grilled oysters, wagyu skewers, tamagoyaki (sweet omelet), and kitchenware.",
        "opening_hours": "06:00 - 14:00 (ร้านส่วนใหญ่ปิดวันพุธและอาทิตย์)",
        "admission_fee": "เข้าชมฟรี",
        "nearest_station_id": "ST_TSUKIJI",
        "walk_time_min": 4
    },
    {
        "place_id": "P_UENO_PARK",
        "name_th": "สวนอุเอโนะและพิพิธภัณฑ์แห่งชาติ",
        "name_en": "Ueno Park & National Museum",
        "name_ja": "上野恩賜公園",
        "ward": "Taito",
        "category": "Culture & Museum",
        "latitude": 35.715368,
        "longitude": 139.773950,
        "description_th": "สวนสาธารณะขนาดใหญ่ที่มีความสำคัญทางวัฒนธรรม ภายในเป็นที่ตั้งของสระบัวชิโนบาซุ (Shinobazu Pond) สวนสัตว์อุเอโนะซึ่งมีแพนด้าชื่อดัง และพิพิธภัณฑ์ชั้นนำของญี่ปุ่น ได้แก่ พิพิธภัณฑ์แห่งชาติโตเกียว (Tokyo National Museum) และพิพิธภัณฑ์ศิลปะตะวันตกแห่งชาติ (NMWA)",
        "description_en": "A sprawling cultural park home to prestigious institutions including the Tokyo National Museum, National Museum of Western Art, Shinobazu Lotus Pond, and Ueno Zoo.",
        "opening_hours": "05:00 - 23:00 (สวนเปิด) / พิพิธภัณฑ์เปิด 09:30 - 17:00",
        "admission_fee": "เข้าสวนฟรี / ตั๋วเข้าพิพิธภัณฑ์เริ่มต้น 1,000 เยน",
        "nearest_station_id": "ST_UENO",
        "walk_time_min": 2
    },
    {
        "place_id": "P_ROPPONGI_HILLS",
        "name_th": "รปปงงิฮิลส์และจุดชมวิวโตเกียวซิตี้วิว",
        "name_en": "Roppongi Hills & Tokyo City View",
        "name_ja": "六本木ヒルズ",
        "ward": "Minato",
        "category": "Landmark & Viewpoint",
        "latitude": 35.660464,
        "longitude": 139.729249,
        "description_th": "อาคารมิกซ์ยูสระดับไฮเอนด์ที่มี Mori Tower สูง 54 ชั้น ด้านบนเป็นที่ตั้งของพิพิธภัณฑ์ศิลปะ Mori Art Museum และจุดชมวิว Tokyo City View ที่มองเห็นโตเกียวทาวเวอร์ในมุมมองที่งดงามที่สุดจุดหนึ่งของโตเกียว ด้านล่างมีประติมากรรมแมงมุมยักษ์ Maman และร้านอาหารระดับมิชลิน",
        "description_en": "A modern urban complex centered around the 54-story Mori Tower, featuring the acclaimed Mori Art Museum and Tokyo City View indoor/outdoor observation deck with iconic vantage points of Tokyo Tower.",
        "opening_hours": "10:00 - 22:00",
        "admission_fee": "จุดชมวิวและพิพิธภัณฑ์ผู้ใหญ่ประมาณ 2,000 เยน",
        "nearest_station_id": "ST_ROPPONGI",
        "walk_time_min": 3
    },
    {
        "place_id": "P_GINZA_SIX",
        "name_th": "ย่านช้อปปิ้งกินซ่าและห้างกินซ่าซิกซ์",
        "name_en": "Ginza Shopping District & GINZA SIX",
        "name_ja": "銀座SIX",
        "ward": "Chuo",
        "category": "Shopping & Entertainment",
        "latitude": 35.669611,
        "longitude": 139.764024,
        "description_th": "ย่านการค้าสุดหรูหราอันดับหนึ่งของญี่ปุ่น เรียงรายด้วยแฟลกชิปสโตร์ของแบรนด์เนมระดับโลก ห้างสรรพสินค้าเก่าแก่ และห้าง GINZA SIX ที่มีการจัดแสดงงานศิลปะร่วมสมัย เช่น ผลงานโคมฟักทองของ Yayoi Kusama บนดาดฟ้ามีสวนสาธารณะลอยฟ้า Ginza Six Garden",
        "description_en": "Tokyo's premier luxury shopping boulevard, home to global flagship boutiques, traditional department stores, and the upscale GINZA SIX complex with contemporary art installations and rooftop garden.",
        "opening_hours": "10:30 - 20:30",
        "admission_fee": "เข้าชมฟรี",
        "nearest_station_id": "ST_GINZA",
        "walk_time_min": 2
    },
    {
        "place_id": "P_ODAIBA_GUNDAM",
        "name_th": "โอไดบะและหุ่นยนต์กันดั้มยักษ์ยูนิคอร์น",
        "name_en": "Odaiba & Unicorn Gundam Statue",
        "name_ja": "お台場 ユニコーンガンダム",
        "ward": "Minato",
        "category": "Shopping & Entertainment",
        "latitude": 35.624444,
        "longitude": 139.775556,
        "description_th": "เกาะเทียมริมอ่าวโตเกียว แหล่งรวมความบันเทิงยอดนิยม มีไฮไลต์คือหุ่นยนต์กันดั้มขนาดเท่าของจริง Life-sized Unicorn Gundam สูง 19.7 เมตร หน้าห้าง DiverCity Tokyo Plaza ซึ่งจะมีการแปลงร่างจากโหมด Unicorn เป็น Destroy Mode พร้อมแสดงแสงสีเสียงทุกวัน นอกจากนี้ยังมีสะพานสายรุ้ง (Rainbow Bridge) และเทพีเสรีภาพจำลอง",
        "description_en": "A futuristic entertainment island on Tokyo Bay featuring the full-scale 19.7-meter Unicorn Gundam statue outside DiverCity Tokyo Plaza, the scenic Rainbow Bridge, and beachside promenades.",
        "opening_hours": "ชมหุ่นยนต์เปิด 24 ชั่วโมง / การแสดงแสงสีเสียงช่วงค่ำ (19:00 - 21:30)",
        "admission_fee": "ชมฟรี",
        "nearest_station_id": "ST_ODAIBA_KAIHINKOEN",
        "walk_time_min": 5
    }
]

# ความสัมพันธ์การเดินระหว่างสถานที่และสถานีรถไฟ (Place to Station Edges)
PLACE_STATION_EDGES = [
    {"place_id": "P_SENSOJI", "station_id": "ST_ASAKUSA", "walk_time_min": 5, "distance_m": 350, "exit_info": "Exit 1 (Tokyo Metro Ginza Line)"},
    {"place_id": "P_TOKYO_SKYTREE", "station_id": "ST_OSHIAGE", "walk_time_min": 2, "distance_m": 150, "exit_info": "Direct Underground Link to Solamachi"},
    {"place_id": "P_SHIBUYA_CROSSING", "station_id": "ST_SHIBUYA", "walk_time_min": 1, "distance_m": 50, "exit_info": "Hachiko Exit"},
    {"place_id": "P_MEIJI_JINGU", "station_id": "ST_HARAJUKU", "walk_time_min": 3, "distance_m": 200, "exit_info": "Omotesando Exit"},
    {"place_id": "P_TOKYO_TOWER", "station_id": "ST_HAMAMATSUCHO", "walk_time_min": 15, "distance_m": 1100, "exit_info": "North Exit"},
    {"place_id": "P_SHINJUKU_GYOEN", "station_id": "ST_SHINJUKU_GYOEMMAE", "walk_time_min": 5, "distance_m": 350, "exit_info": "Exit 1 (Shinjuku Gate)"},
    {"place_id": "P_AKIHABARA_ELECTRIC", "station_id": "ST_AKIHABARA", "walk_time_min": 1, "distance_m": 80, "exit_info": "Electric Town Exit"},
    {"place_id": "P_TSUKIJI_OUTER", "station_id": "ST_TSUKIJI", "walk_time_min": 4, "distance_m": 300, "exit_info": "Exit 1"},
    {"place_id": "P_UENO_PARK", "station_id": "ST_UENO", "walk_time_min": 2, "distance_m": 120, "exit_info": "Park Exit"},
    {"place_id": "P_ROPPONGI_HILLS", "station_id": "ST_ROPPONGI", "walk_time_min": 3, "distance_m": 250, "exit_info": "Exit 1C (Direct Concourse)"},
    {"place_id": "P_GINZA_SIX", "station_id": "ST_GINZA", "walk_time_min": 2, "distance_m": 180, "exit_info": "Exit A3"},
    {"place_id": "P_ODAIBA_GUNDAM", "station_id": "ST_ODAIBA_KAIHINKOEN", "walk_time_min": 5, "distance_m": 400, "exit_info": "North Exit"}
]
