"""
Curated Tokyo Tourism, Transit & Accommodation Dataset
รวบรวมข้อมูลสถานที่ท่องเที่ยว สถานีรถไฟ สายรถไฟ โครงข่ายการเดินทาง และโรงแรมที่พักในโตเกียว
อ้างอิงจาก JTA Sightseeing Database, 駅データ.jp, OpenStreetMap และ e-Gov Tourism Statistics
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
    },
    {
        "line_id": "LN_CHIYODA",
        "name_th": "รถไฟใต้ดินสายชิโยดะ (Tokyo Metro Chiyoda Line)",
        "name_en": "Tokyo Metro Chiyoda Line",
        "line_code": "C",
        "operator": "Tokyo Metro",
        "color": "#00BB85"  # Green
    },
    {
        "line_id": "LN_NAMBOKU",
        "name_th": "รถไฟใต้ดินสายนะนโบกุ (Tokyo Metro Namboku Line)",
        "name_en": "Tokyo Metro Namboku Line",
        "line_code": "N",
        "operator": "Tokyo Metro",
        "color": "#00AC9B"  # Emerald
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
    },
    {
        "station_id": "ST_OMOTESANDO",
        "name_th": "สถานีโอโมเตะซันโด",
        "name_en": "Omotesando Station",
        "name_ja": "表参道駅",
        "lines": "LN_GINZA;LN_HANZOMON;LN_CHIYODA",
        "ward": "Minato",
        "latitude": 35.665247,
        "longitude": 139.712314
    },
    {
        "station_id": "ST_KORAKUEN",
        "name_th": "สถานีโคระคุเอ็น (โตเกียวโดม)",
        "name_en": "Korakuen Station",
        "name_ja": "後楽園駅",
        "lines": "LN_MARUNOUCHI;LN_NAMBOKU;LN_OEDO",
        "ward": "Bunkyo",
        "latitude": 35.707328,
        "longitude": 139.751682
    },
    {
        "station_id": "ST_SHIJO_MAE",
        "name_th": "สถานีชิโจมาเอะ (ตลาดปลาโทโยสุ)",
        "name_en": "Shijo-mae Station",
        "name_ja": "市場前駅",
        "lines": "LN_YURIKAMOME",
        "ward": "Koto",
        "latitude": 35.645389,
        "longitude": 139.784444
    }
]

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
    {"from_station_id": "ST_SHIBUYA", "to_station_id": "ST_OMOTESANDO", "line_id": "LN_GINZA", "line_name": "Tokyo Metro Ginza Line", "duration_min": 2, "distance_km": 1.3},
    {"from_station_id": "ST_OMOTESANDO", "to_station_id": "ST_GINZA", "line_id": "LN_GINZA", "line_name": "Tokyo Metro Ginza Line", "duration_min": 14, "distance_km": 5.4},
    {"from_station_id": "ST_GINZA", "to_station_id": "ST_SHIMBASHI", "line_id": "LN_GINZA", "line_name": "Tokyo Metro Ginza Line", "duration_min": 2, "distance_km": 0.9},
    {"from_station_id": "ST_GINZA", "to_station_id": "ST_UENO", "line_id": "LN_GINZA", "line_name": "Tokyo Metro Ginza Line", "duration_min": 12, "distance_km": 4.5},
    {"from_station_id": "ST_UENO", "to_station_id": "ST_ASAKUSA", "line_id": "LN_GINZA", "line_name": "Tokyo Metro Ginza Line", "duration_min": 5, "distance_km": 2.2},

    # 3. Tokyo Metro Marunouchi Line
    {"from_station_id": "ST_IKEBUKURO", "to_station_id": "ST_KORAKUEN", "line_id": "LN_MARUNOUCHI", "line_name": "Tokyo Metro Marunouchi Line", "duration_min": 7, "distance_km": 3.8},
    {"from_station_id": "ST_KORAKUEN", "to_station_id": "ST_TOKYO", "line_id": "LN_MARUNOUCHI", "line_name": "Tokyo Metro Marunouchi Line", "duration_min": 9, "distance_km": 4.2},
    {"from_station_id": "ST_TOKYO", "to_station_id": "ST_GINZA", "line_id": "LN_MARUNOUCHI", "line_name": "Tokyo Metro Marunouchi Line", "duration_min": 3, "distance_km": 1.1},
    {"from_station_id": "ST_GINZA", "to_station_id": "ST_SHINJUKU_GYOEMMAE", "line_id": "LN_MARUNOUCHI", "line_name": "Tokyo Metro Marunouchi Line", "duration_min": 13, "distance_km": 5.9},
    {"from_station_id": "ST_SHINJUKU_GYOEMMAE", "to_station_id": "ST_SHINJUKU", "line_id": "LN_MARUNOUCHI", "line_name": "Tokyo Metro Marunouchi Line", "duration_min": 3, "distance_km": 1.1},

    # 4. Tokyo Metro Hibiya Line
    {"from_station_id": "ST_UENO", "to_station_id": "ST_AKIHABARA", "line_id": "LN_HIBIYA", "line_name": "Tokyo Metro Hibiya Line", "duration_min": 3, "distance_km": 1.6},
    {"from_station_id": "ST_AKIHABARA", "to_station_id": "ST_GINZA", "line_id": "LN_HIBIYA", "line_name": "Tokyo Metro Hibiya Line", "duration_min": 9, "distance_km": 3.7},
    {"from_station_id": "ST_GINZA", "to_station_id": "ST_TSUKIJI", "line_id": "LN_HIBIYA", "line_name": "Tokyo Metro Hibiya Line", "duration_min": 3, "distance_km": 1.4},
    {"from_station_id": "ST_GINZA", "to_station_id": "ST_ROPPONGI", "line_id": "LN_HIBIYA", "line_name": "Tokyo Metro Hibiya Line", "duration_min": 9, "distance_km": 4.1},

    # 5. Toei Asakusa Line & Hanzomon Line
    {"from_station_id": "ST_ASAKUSA", "to_station_id": "ST_OSHIAGE", "line_id": "LN_ASAKUSA", "line_name": "Toei Asakusa Line", "duration_min": 3, "distance_km": 1.5},
    {"from_station_id": "ST_SHIMBASHI", "to_station_id": "ST_ASAKUSA", "line_id": "LN_ASAKUSA", "line_name": "Toei Asakusa Line", "duration_min": 14, "distance_km": 6.8},
    {"from_station_id": "ST_SHIBUYA", "to_station_id": "ST_OMOTESANDO", "line_id": "LN_HANZOMON", "line_name": "Tokyo Metro Hanzomon Line", "duration_min": 2, "distance_km": 1.3},
    {"from_station_id": "ST_OMOTESANDO", "to_station_id": "ST_OSHIAGE", "line_id": "LN_HANZOMON", "line_name": "Tokyo Metro Hanzomon Line", "duration_min": 29, "distance_km": 13.9},

    # 6. Toei Oedo Line
    {"from_station_id": "ST_SHINJUKU", "to_station_id": "ST_ROPPONGI", "line_id": "LN_OEDO", "line_name": "Toei Oedo Line", "duration_min": 9, "distance_km": 4.5},
    {"from_station_id": "ST_ROPPONGI", "to_station_id": "ST_HAMAMATSUCHO", "line_id": "LN_OEDO", "line_name": "Toei Oedo Line", "duration_min": 6, "distance_km": 2.8},
    {"from_station_id": "ST_KORAKUEN", "to_station_id": "ST_SHINJUKU", "line_id": "LN_OEDO", "line_name": "Toei Oedo Line", "duration_min": 14, "distance_km": 6.2},

    # 7. JR Chuo-Sobu Line
    {"from_station_id": "ST_SHINJUKU", "to_station_id": "ST_AKIHABARA", "line_id": "LN_CHUO_SOBU", "line_name": "JR Chuo-Sobu Line", "duration_min": 12, "distance_km": 6.7},

    # 8. Yurikamome Line
    {"from_station_id": "ST_SHIMBASHI", "to_station_id": "ST_ODAIBA_KAIHINKOEN", "line_id": "LN_YURIKAMOME", "line_name": "Yurikamome Line", "duration_min": 13, "distance_km": 5.0},
    {"from_station_id": "ST_ODAIBA_KAIHINKOEN", "to_station_id": "ST_SHIJO_MAE", "line_id": "LN_YURIKAMOME", "line_name": "Yurikamome Line", "duration_min": 9, "distance_km": 3.9},
    {"from_station_id": "ST_SHIJO_MAE", "to_station_id": "ST_TOYOSU", "line_id": "LN_YURIKAMOME", "line_name": "Yurikamome Line", "duration_min": 4, "distance_km": 1.8}
]

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
        "description_th": "วัดเซ็นโซจิเป็นวัดพุทธที่เก่าแก่ที่สุดในกรุงโตเกียว สร้างขึ้นในปี ค.ศ. 628 มีเอกลักษณ์คือประตูคามินาริโมง (Kaminarimon) ที่แขวนโคมแดงยักษ์อันเลื่องชื่อ ภายในมีถนนคนเดินนากามิเสะ (Nakamise-dori) ทอดยาวกว่า 250 เมตร เต็มไปด้วยร้านขายขนมพื้นเมือง เช่น ขนมเซมเบ้ มันจูทอด ขนมปังเมลอน และของที่ระลึกดั้งเดิม เป็นจุดหมายยอดนิยมที่ผู้คนมาสักการะองค์เจ้าแม่กวนอิมเพื่อขอพรเรื่องความสุขและความสำเร็จ",
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
    },
    # --- ข้อมูลเพิ่มเติมรอบใหม่ 8 แห่ง (จาก JTA Sightseeing Database & OSM) ---
    {
        "place_id": "P_IMPERIAL_PALACE",
        "name_th": "พระราชวังอิมพีเรียลโตเกียวและสวนโคเคียวฮิกาชิ",
        "name_en": "Tokyo Imperial Palace & East Gardens",
        "name_ja": "皇居",
        "ward": "Chiyoda",
        "category": "Culture & History",
        "latitude": 35.685175,
        "longitude": 139.752800,
        "description_th": "พระราชวังอิมพีเรียลเป็นที่ประทับหลักของสมเด็จพระจักรพรรดิแห่งญี่ปุ่น ตั้งอยู่ใจกลางกรุงโตเกียวบนพื้นที่เดิมของปราสาทเอโดะ (Edo Castle) ล้อมรอบด้วยคูน้ำโบราณ กำแพงหินขนาดยักษ์ และสะพานแว่นตานิจูบาชิ (Nijubashi Bridge) อันเลื่องชื่อ บริเวณสวนฝั่งตะวันออก (East Gardens) เปิดให้นักท่องเที่ยวเข้าชมฟรี มีซากฐานป้อมปราการหอคอยปราสาทเอโดะ สวนสไตล์ญี่ปุ่นดั้งเดิม และต้นซากุระมากมาย เหมาะสำหรับการเดินเล่นและเรียนรู้ประวัติศาสตร์",
        "description_en": "The Imperial Palace is the primary residence of the Emperor of Japan, built on the former site of Edo Castle. Surrounded by scenic moats, massive stone ramparts, and the iconic Nijubashi Bridge. The East Gardens are open to the public free of charge, showcasing historic castle foundations and tranquil Japanese gardens.",
        "opening_hours": "09:00 - 17:00 (ปิดวันจันทร์และวันศุกร์)",
        "admission_fee": "เข้าชมสวนฟรี (การเข้าชมพระราชวังด้านในต้องจองล่วงหน้า)",
        "nearest_station_id": "ST_TOKYO",
        "walk_time_min": 10
    },
    {
        "place_id": "P_TEAMLAB_PLANETS",
        "name_th": "พิพิธภัณฑ์ศิลปะดิจิทัลทีมแล็บ แพลเน็ตส์ โตเกียว",
        "name_en": "teamLab Planets TOKYO DMM",
        "name_ja": "チームラボプラネッツ TOKYO",
        "ward": "Koto",
        "category": "Culture & Art",
        "latitude": 35.649067,
        "longitude": 139.789725,
        "description_th": "พิพิธภัณฑ์ศิลปะดิจิทัลแบบอินเทอร์แอคทีฟระดับโลกที่ผู้เข้าชมต้องถอดรองเท้าเดินลุยน้ำ มีแนวคิด 'Body Immersive' ผสานร่างกายเข้ากับงานศิลปะแสง สี เสียง ไฮไลต์เด่นได้แก่ ห้องสวนดอกกล้วยไม้มีชีวิตลอยได้ (Floating Flower Garden) ห้องคริสตัลกระจกไร้ที่สิ้นสุด (The Infinite Crystal Universe) และผืนน้ำที่ฉายภาพปลาคาร์ปแหวกว่ายเปลี่ยนเป็นดอกไม้เมื่อสัมผัส",
        "description_en": "A world-renowned immersive digital art museum where visitors walk barefoot through water. Features iconic exhibits including The Infinite Crystal Universe, Floating Flower Garden with thousands of living orchids, and interactive water installations.",
        "opening_hours": "09:00 - 22:00 (รอบสุดท้าย 21:00)",
        "admission_fee": "ผู้ใหญ่เริ่มต้น 3,800 - 4,200 เยน (แนะนำจองตั๋วออนไลน์ล่วงหน้า)",
        "nearest_station_id": "ST_TOYOSU",
        "walk_time_min": 10
    },
    {
        "place_id": "P_AMEYOKO",
        "name_th": "ตลาดอะเมโยโกะ (ถนนคนเดินอะเมยะ โยโกโจ)",
        "name_en": "Ameyoko Shopping Street",
        "name_ja": "アメヤ横丁",
        "ward": "Taito",
        "category": "Food & Market",
        "latitude": 35.711202,
        "longitude": 139.774577,
        "description_th": "ถนนคนเดินและตลาดกลางแจ้งอันคึกคักใต้รางรถไฟระหว่างสถานีอุเอโนะและสถานีโอคาจิมาจิ เดิมเป็นตลาดมืดหลังสงครามโลก ปัจจุบันเต็มไปด้วยร้านขายอาหารสตรีทฟู้ด ข้าวหน้าปลาดิบราคาประหยัด ผลไม้เสียบไม้สด ผลไม้อบแห้ง เสื้อผ้า รองเท้าผ้าใบ และขนมของฝากยอดนิยมในราคาย่อมเยา มีกลิ่นอายความมีชีวิตชีวาแบบดั้งเดิมของโตเกียว",
        "description_en": "A vibrant open-air market street running along the elevated train tracks between Ueno and Okachimachi stations. Famous for bustling street food vendors, fresh seafood stalls, inexpensive sneakers, cosmetics, and traditional sweets.",
        "opening_hours": "10:00 - 20:00 (ขึ้นอยู่กับแต่ละร้านค้า)",
        "admission_fee": "เข้าชมฟรี",
        "nearest_station_id": "ST_UENO",
        "walk_time_min": 2
    },
    {
        "place_id": "P_TAKESHITA_STREET",
        "name_th": "ถนนทาเคชิตะ ย่านฮาราจูกุ",
        "name_en": "Takeshita Street Harajuku",
        "name_ja": "竹下通り",
        "ward": "Shibuya",
        "category": "Shopping & Entertainment",
        "latitude": 35.671607,
        "longitude": 139.703247,
        "description_th": "ศูนย์กลางแฟชั่นวัยรุ่นและวัฒนธรรมคาวาอี้ (Kawaii Culture) ระดับตำนานของญี่ปุ่น ถนนคนเดินความยาว 400 เมตร แน่นขนัดไปด้วยร้านเสื้อผ้าแฟชั่นสตรีทแวร์ ร้านขายของกุ๊กกิ๊ก คาเฟ่สัตว์เลี้ยง และร้านเครปญี่ปุ่นม้วนสดชื่อดังอย่าง Marion Crepes และ Santa Monica Crepes รวมถึงสายไหมสีรุ้งขนาดยักษ์",
        "description_en": "The pulsating epicenter of Japanese youth pop culture and kawaii fashion. This 400-meter pedestrian avenue is packed with quirky boutiques, trendy streetwear, vintage shops, rainbow cotton candy, and Harajuku's legendary sweet crepe stalls.",
        "opening_hours": "10:00 - 20:00",
        "admission_fee": "เข้าชมฟรี",
        "nearest_station_id": "ST_HARAJUKU",
        "walk_time_min": 1
    },
    {
        "place_id": "P_HAMARIKYU_GARDENS",
        "name_th": "สวนฮามาริคิว (สวนหลวงริมอ่าวโตเกียว)",
        "name_en": "Hamarikyu Gardens",
        "name_ja": "浜離宮恩賜庭園",
        "ward": "Chuo",
        "category": "Nature & Park",
        "latitude": 35.659722,
        "longitude": 139.763333,
        "description_th": "สวนสาธารณะสไตล์ญี่ปุ่นโบราณในยุคเอโดะของตระกูลโชกุนโทกูงาวะ มีเอกลักษณ์โดดเด่นคือสระน้ำชิโออิริ (Shioiri-no-ike) ซึ่งเป็นสระน้ำเค็มที่รับน้ำขึ้นน้ำลงจากอ่าวโตเกียวโดยตรง กลางสระมีโรงน้ำชาโบราณ Nakajima no Ochaya ที่นักท่องเที่ยวสามารถนั่งจิบชาเขียวมัทฉะคู่กับขนมวากาชิ พร้อมชมทิวทัศน์ความตัดกันระหว่างสวนโบราณกับตึกระฟ้าของย่านชิโอโดเมะ",
        "description_en": "A tranquil traditional Edo-period Japanese landscape garden on Tokyo Bay, formerly belonging to the Tokugawa Shogun family. Features tidal seawater ponds and a charming teahouse on the water serving matcha tea against a dramatic backdrop of Shiodome skyscrapers.",
        "opening_hours": "09:00 - 17:00",
        "admission_fee": "ผู้ใหญ่ 300 เยน",
        "nearest_station_id": "ST_SHIMBASHI",
        "walk_time_min": 10
    },
    {
        "place_id": "P_TOKYO_DOME_CITY",
        "name_th": "โตเกียวโดมซิตี้และสปาลาคัว",
        "name_en": "Tokyo Dome City & Spa LaQua",
        "name_ja": "東京ドームシティ",
        "ward": "Bunkyo",
        "category": "Shopping & Entertainment",
        "latitude": 35.705639,
        "longitude": 139.751889,
        "description_th": "อาณาจักรความบันเทิงครบวงจรใจกลางโตเกียว ประกอบด้วยสนามเบสบอลและฮอลล์คอนเสิร์ตระดับโลก 'Tokyo Dome' สวนสนุก Tokyo Dome City Attractions ที่มีรถไฟเหาะ Thunder Dolphin ทะลุตึก และชิงช้าสวรรค์ Big O รวมถึงคอมเพล็กซ์ 'Spa LaQua' บ่อน้ำพุร้อนออนเซ็นธรรมชาติแท้ๆ จากใต้ดินลึก 1,700 เมตร พร้อมซาวน่าและร้านอาหารเพื่อการผ่อนคลาย",
        "description_en": "A vast entertainment and leisure hub featuring the iconic Tokyo Dome baseball stadium and concert venue, an amusement park with the Thunder Dolphin rollercoaster through a building, and Spa LaQua luxury natural hot springs onsen complex.",
        "opening_hours": "10:00 - 21:00 (Spa LaQua เปิด 11:00 - 09:00 เช้าวันถัดไป)",
        "admission_fee": "เข้าบริเวณฟรี / ค่าเครื่องเล่นหรือค่าสปาแยกตามจุดบริการ (Spa LaQua ประมาณ 3,230 เยน)",
        "nearest_station_id": "ST_KORAKUEN",
        "walk_time_min": 3
    },
    {
        "place_id": "P_TOYOSU_MARKET",
        "name_th": "ตลาดปลาโทโยสุและคอมเพล็กซ์เซ็นเคียคุบันไร",
        "name_en": "Toyosu Fish Market & Toyosu Senkyaku Banrai",
        "name_ja": "豊洲市場・千客万来",
        "ward": "Koto",
        "category": "Food & Market",
        "latitude": 35.646111,
        "longitude": 139.785278,
        "description_th": "ตลาดค้าส่งสัตว์น้ำและอาหารที่ใหญ่และทันสมัยที่สุดในโลกที่ย้ายมาจากสึกิจิ มีจุดชมการประมูลปลาทูน่ายามเช้าอันเลื่องชื่อ และโซนเปิดใหม่ 'Toyosu Senkyaku Banrai' ซึ่งเป็นเมืองจำลองสไตล์เอโดะย้อนยุค รวมร้านอาหารซูชิ ซาชิมิระดับพรีเมียม อาหารทะเลปิ้งย่างกว่า 60 ร้าน พร้อมอาคารบ่อออนเซ็นแช่น้ำแร่ธรรมชาติชมวิวอ่าวโตเกียว",
        "description_en": "The world's largest state-of-the-art wholesale seafood market, successor to historic Tsukiji. Features the famous early-morning tuna auctions, top-tier sushi eateries, and the newly opened Senkyaku Banrai Edo-themed dining and natural onsen hot spring promenade.",
        "opening_hours": "05:00 - 15:00 (ตลาดค้าส่ง) / 10:00 - 22:00 (โซน Senkyaku Banrai)",
        "admission_fee": "เข้าชมฟรี",
        "nearest_station_id": "ST_SHIJO_MAE",
        "walk_time_min": 2
    },
    {
        "place_id": "P_OMOTESANDO_HILLS",
        "name_th": "ถนนสายช้อปปิ้งโอโมเตะซันโดและห้างโอโมเตะซันโดฮิลส์",
        "name_en": "Omotesando Boulevard & Omotesando Hills",
        "name_ja": "表参道ヒルズ",
        "ward": "Shibuya",
        "category": "Shopping & Entertainment",
        "latitude": 35.667111,
        "longitude": 139.709972,
        "description_th": "ถนนสายช้อปปิ้งต้นเซลโคว่าอันร่มรื่นที่ได้รับการขนานนามว่าเป็น 'ช็องเซลิเซ่แห่งโตเกียว' ศูนย์รวมแฟลกชิปสโตร์ของแบรนด์แฟชั่นระดับไฮเอนด์และสถาปัตยกรรมระดับมาสเตอร์พีซ ออกแบบโดยสถาปนิกชื่อดังระดับโลก เช่น Tadao Ando ผู้รังสรรค์ห้าง Omotesando Hills ที่มีทางลาดวนอันเป็นเอกลักษณ์ รายล้อมด้วยคาเฟ่เบเกอรี่สไตล์ยุโรปและร้านกาแฟบูทีก",
        "description_en": "Tokyo's leafy 'Champs-Elysees', renowned for striking avant-garde architecture, world-class luxury brand flagships, and the Tadao Ando-designed Omotesando Hills shopping complex with its continuous spiraling ramp and chic European cafes.",
        "opening_hours": "11:00 - 21:00",
        "admission_fee": "เข้าชมฟรี",
        "nearest_station_id": "ST_OMOTESANDO",
        "walk_time_min": 2
    }
]

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
    {"place_id": "P_ODAIBA_GUNDAM", "station_id": "ST_ODAIBA_KAIHINKOEN", "walk_time_min": 5, "distance_m": 400, "exit_info": "North Exit"},
    # --- เส้นเชื่อมใหม่ 8 แห่ง ---
    {"place_id": "P_IMPERIAL_PALACE", "station_id": "ST_TOKYO", "walk_time_min": 10, "distance_m": 800, "exit_info": "Marunouchi Central Exit"},
    {"place_id": "P_TEAMLAB_PLANETS", "station_id": "ST_TOYOSU", "walk_time_min": 10, "distance_m": 750, "exit_info": "Exit 7 (or 1 min from Shin-Toyosu Station)"},
    {"place_id": "P_AMEYOKO", "station_id": "ST_UENO", "walk_time_min": 2, "distance_m": 150, "exit_info": "Shinobazu Exit"},
    {"place_id": "P_TAKESHITA_STREET", "station_id": "ST_HARAJUKU", "walk_time_min": 1, "distance_m": 50, "exit_info": "Takeshita Exit"},
    {"place_id": "P_HAMARIKYU_GARDENS", "station_id": "ST_SHIMBASHI", "walk_time_min": 10, "distance_m": 750, "exit_info": "Shiodome Exit"},
    {"place_id": "P_TOKYO_DOME_CITY", "station_id": "ST_KORAKUEN", "walk_time_min": 3, "distance_m": 200, "exit_info": "Exit 2"},
    {"place_id": "P_TOYOSU_MARKET", "station_id": "ST_SHIJO_MAE", "walk_time_min": 2, "distance_m": 100, "exit_info": "Direct Covered Pedestrian Concourse"},
    {"place_id": "P_OMOTESANDO_HILLS", "station_id": "ST_OMOTESANDO", "walk_time_min": 2, "distance_m": 180, "exit_info": "Exit A2"}
]

# ข้อมูลโรงแรมและที่พัก (Hotels & Accommodations Dataset) จาก e-Gov Syukuhaku & Tokyo Tourism Data
HOTELS_DATA = [
    {
        "hotel_id": "H_GRACERY_SHINJUKU",
        "name_th": "โรงแรมเกรเซอรี ชินจูกุ (โรงแรมก็อดซิลล่า)",
        "name_en": "Hotel Gracery Shinjuku",
        "name_ja": "ホテルグレイスリー新宿",
        "ward": "Shinjuku",
        "tier": "Mid-Scale / Business",
        "price_range": "3,500 - 6,500 บาท/คืน",
        "nearest_station_id": "ST_SHINJUKU",
        "walk_time_min": 5,
        "highlights": "หัวก็อดซิลล่าขนาดยักษ์บนระเบียงชั้น 8 ย่านคาบูกิโจ เดินทางสะดวกใกล้สถานีชินจูกุ",
        "description_th": "โรงแรมแลนด์มาร์กยอดนิยมใจกลางย่านคาบูกิโจ ชินจูกุ มีหัวก็อดซิลล่าขนาดยักษ์พ่นควันส่งเสียงคำราม ห้องพักสะอาดทันสมัย แยกห้องอาบน้ำและห้องส้วมสไตล์ญี่ปุ่น ใกล้ร้านอาหาร แหล่งช้อปปิ้ง และสถานีรถไฟชินจูกุ",
        "description_en": "Iconic hotel in Kabukicho, Shinjuku featuring a life-sized Godzilla head on the terrace. Modern rooms with Japanese-style bathrooms, walking distance to Shinjuku Station."
    },
    {
        "hotel_id": "H_TOKYO_STATION_HOTEL",
        "name_th": "โรงแรมเดอะ โตเกียว สเตชั่น โฮเทล",
        "name_en": "The Tokyo Station Hotel",
        "name_ja": "東京ステーションホテル",
        "ward": "Chiyoda",
        "tier": "Luxury",
        "price_range": "15,000 - 30,000 บาท/คืน",
        "nearest_station_id": "ST_TOKYO",
        "walk_time_min": 1,
        "highlights": "โรงแรมระดับ 5 ดาวภายในอาคารอิฐแดงสถานีโตเกียว สถาปัตยกรรมคลาสสิกตั้งแต่ปี 1915",
        "description_th": "โรงแรมหรูระดับตำนานตั้งอยู่ภายในอาคารประวัติศาสตร์อิฐแดงของสถานีโตเกียว ออกแบบสไตล์ยุโรปคลาสสิก เพดานสูง โปร่งสบาย บริการระดับเวิลด์คลาส เชื่อมต่อกับรถไฟชินคันเซ็นและสายต่างๆ ได้ทันที",
        "description_en": "A prestigious 5-star luxury hotel located inside the iconic red-brick Tokyo Station building dating back to 1915. Direct access to Shinkansen and Tokyo Metro."
    },
    {
        "hotel_id": "H_SHIBUYA_STREAM_EXCEL",
        "name_th": "ชิบูย่า สตรีม เอ็กเซล โฮเทล โทคิว",
        "name_en": "Shibuya Stream Excel Hotel Tokyu",
        "name_ja": "渋谷ストリームエクセルホテル東急",
        "ward": "Shibuya",
        "tier": "Mid-Scale / Business",
        "price_range": "5,500 - 9,500 บาท/คืน",
        "nearest_station_id": "ST_SHIBUYA",
        "walk_time_min": 2,
        "highlights": "เชื่อมตรงกับสถานีชิบูย่า ดีไซน์โมเดิร์นวินเทจ อยู่ในคอมเพล็กซ์ Shibuya Stream",
        "description_th": "โรงแรมทันสมัยใจกลางชิบูย่า เชื่อมตรงสู่สถานีชิบูย่าโดยไม่ต้องออกนอกอาคาร รายล้อมด้วยร้านอาหาร คาเฟ่ริมลำธารชิบูย่า และห้าแยกชิบูย่า",
        "description_en": "Stylish design hotel directly connected to Shibuya Station, featuring vintage-modern decor and convenient access to Shibuya Crossing and dining complexes."
    },
    {
        "hotel_id": "H_ASAKUSA_VIEW",
        "name_th": "โรงแรมอาซากุสะ วิว โฮเทล",
        "name_en": "Asakusa View Hotel",
        "name_ja": "浅草ビューホテル",
        "ward": "Taito",
        "tier": "Mid-Scale / Business",
        "price_range": "3,000 - 6,000 บาท/คืน",
        "nearest_station_id": "ST_ASAKUSA",
        "walk_time_min": 6,
        "highlights": "วิวพาโนรามาเห็นทั้งวัดเซ็นโซจิและโตเกียวสกายทรี อาหารเช้าบุฟเฟต์ชื่อดัง",
        "description_th": "โรงแรมสูงเด่นในย่านอาซากุสะ มีห้องพักที่สามารถชมวิววัดเซ็นโซจิและโตเกียวสกายทรีได้อย่างชัดเจน ใกล้ถนนคนเดินนากามิเสะและสถานีรถไฟ",
        "description_en": "Renowned hotel offering panoramic views of Senso-ji Temple and Tokyo Skytree, famous breakfast buffet and close to traditional shopping streets."
    },
    {
        "hotel_id": "H_CANDEO_UENO",
        "name_th": "คันเดโอ โฮเทลส์ อุเอโนะ พาร์ค",
        "name_en": "Candeo Hotels Ueno Park",
        "name_ja": "カンデオホテルズ上野公園",
        "ward": "Taito",
        "tier": "Budget / Mid-Scale",
        "price_range": "2,500 - 4,500 บาท/คืน",
        "nearest_station_id": "ST_UENO",
        "walk_time_min": 6,
        "highlights": "ราคาย่อมเยา ใกล้สวนอุเอโนะ ตลาดอะเมโยโกะ และรถไฟ Keisei Skyliner สู่สนามบินนาริตะ",
        "description_th": "ที่พักคุณภาพเยี่ยมราคาสบายกระเป๋า เตียงนอนสบายตามมาตรฐาน Candeo เดินเพียงไม่กี่นาทีถึงสวนอุเอโนะและตลาดอะเมโยโกะ เหมาะสำหรับนักเดินทางที่ต้องเดินทางไป-กลับสนามบินนาริตะ",
        "description_en": "Comfortable and budget-friendly hotel near Ueno Park, Ameyoko Market, and Keisei Skyliner with swift access to Narita Airport."
    },
    {
        "hotel_id": "H_MITSUI_GARDEN_GINZA",
        "name_th": "โรงแรมมิตซุย การ์เดน กินซ่า พรีเมียร์",
        "name_en": "Mitsui Garden Hotel Ginza Premier",
        "name_ja": "三井ガーデンホテル銀座プレミア",
        "ward": "Chuo",
        "tier": "Luxury / Upper-Scale",
        "price_range": "7,000 - 13,000 บาท/คืน",
        "nearest_station_id": "ST_GINZA",
        "walk_time_min": 7,
        "highlights": "ล็อบบี้ลอยฟ้าชั้น 16 มองเห็นวิวอ่าวโตเกียวและโตเกียวทาวเวอร์ เดินถึงย่านช้อปปิ้งกินซ่า",
        "description_th": "โรงแรมระดับพรีเมียมในย่านกินซ่า ล็อบบี้และบาร์ตั้งอยู่บนชั้นสูงพร้อมวิวระฟ้าอันงดงามของโตเกียวทาวเวอร์ ห้องน้ำมีอ่างแช่ตัวชมวิวเมือง ย่านช้อปปิ้งหรูหรา",
        "description_en": "Chic premier hotel in Ginza with a 16th-floor sky lobby overlooking Tokyo Tower and Tokyo Bay, offering stylish rooms with skyline bathroom views."
    },
    {
        "hotel_id": "H_DORM_INN_AKIHABARA",
        "name_th": "ดอร์มี อินน์ อากิฮาบาระ (พร้อมบ่อออนเซ็น)",
        "name_en": "Dormy Inn Akihabara Hot Springs",
        "name_ja": "すえひろの湯 ドーミーイン秋葉原",
        "ward": "Chiyoda",
        "tier": "Budget / Mid-Scale",
        "price_range": "2,800 - 4,800 บาท/คืน",
        "nearest_station_id": "ST_AKIHABARA",
        "walk_time_min": 5,
        "highlights": "มีบ่อออนเซ็นกลางแจ้งบนดาดฟ้า บริการราเมนราตรี (Yonaki Soba) ฟรีทุกคืน",
        "description_th": "โรงแรมยอดนิยมขวัญใจนักท่องเที่ยว มีบ่อน้ำพุร้อนออนเซ็นกลางแจ้งบนชั้นดาดฟ้าและห้องซาวน่า พร้อมเสิร์ฟราเมงซีอิ๊วญี่ปุ่นร้อนๆ ฟรีช่วงดึก อยู่ใจกลางย่านอนิเมะอากิฮาบาระ",
        "description_en": "Popular hotel in Akihabara featuring open-air rooftop hot spring baths, saunas, and complimentary evening Yonaki Soba ramen."
    },
    {
        "hotel_id": "H_PRINCE_GALLERY_KIOICHO",
        "name_th": "เดอะ ปรินซ์ แกลเลอรี โตเกียว คิโออิโจ (โรงแรม 5 ดาว)",
        "name_en": "The Prince Gallery Tokyo Kioicho, Luxury Collection",
        "name_ja": "ザ・プリンスギャラリー 東京紀尾井町",
        "ward": "Chiyoda",
        "tier": "Ultra Luxury",
        "price_range": "18,000 - 35,000 บาท/คืน",
        "nearest_station_id": "ST_ROPPONGI",
        "walk_time_min": 10,
        "highlights": "โรงแรมหรูบนชั้น 30-36 วิวเมืองโตเกียวแบบพาโนรามา สปา สระว่ายน้ำในร่มกระจกสูง",
        "description_th": "โรงแรมหรูระดับแนวหน้าของโตเกียว ตั้งอยู่บนชั้น 30-36 ของ Tokyo Garden Terrace Kioicho มองเห็นทิวทัศน์มุมกว้างของมหานคร พร้อมสปาระดับไฮเอนด์และห้องอาหารหรู",
        "description_en": "An ultra-luxury hotel on floors 30-36 of Tokyo Garden Terrace Kioicho, offering breathtaking skyline vistas, world-class dining, and an indoor glass swimming pool."
    },
    {
        "hotel_id": "H_SUPER_HOTEL_SHINJUKU",
        "name_th": "ซูเปอร์ โฮเทล ชินจูกุ คาบูกิโจ",
        "name_en": "Super Hotel Shinjuku Kabukicho",
        "name_ja": "スーパーホテル新宿・歌舞伎町",
        "ward": "Shinjuku",
        "tier": "Budget",
        "price_range": "2,000 - 3,500 บาท/คืน",
        "nearest_station_id": "ST_SHINJUKU",
        "walk_time_min": 7,
        "highlights": "บ่อออนเซ็นธรรมชาติในโรงแรม มีหมอนให้เลือก 8 แบบ ราคาสุดคุ้มใจกลางชินจูกุ",
        "description_th": "ที่พักราคาย่อมเยายอดนิยมใจกลางชินจูกุ มีบ่อน้ำพุร้อนออนเซ็นธรรมชาติแยกชาย-หญิงให้แช่ฟรี มีหมอนให้เลือกตามสรีระ อาหารเช้าออร์แกนิกฟรี",
        "description_en": "Excellent value budget hotel in Shinjuku featuring natural hot spring baths, custom pillow selections, and healthy buffet breakfasts."
    },
    {
        "hotel_id": "H_HOTEL_VILLA_FONTAINE_ROPPONGI",
        "name_th": "โรงแรมวิลล่า ฟอนเทน แกรนด์ รปปงงิ",
        "name_en": "Hotel Villa Fontaine Grand Tokyo-Roppongi",
        "name_ja": "ホテルヴィラフォンテーヌグランド東京六本木",
        "ward": "Minato",
        "tier": "Mid-Scale / Business",
        "price_range": "4,000 - 7,000 บาท/คืน",
        "nearest_station_id": "ST_ROPPONGI",
        "walk_time_min": 5,
        "highlights": "เชื่อมต่อตรงสถานีรถไฟ สะดวก ปลอดภัย ใกล้ Roppongi Hills และย่านกินดื่มราตรี",
        "description_th": "โรงแรมสไตล์บิสซิเนสระดับพรีเมียม เชื่อมต่อโดยตรงกับทางออกสถานีรถไฟ สะดวกสบาย เงียบสงบ ปลอดภัย ใกล้ศูนย์การค้า Roppongi Hills และพิพิธภัณฑ์ศิลปะ",
        "description_en": "Business-chic hotel directly connected to the subway station, walking distance to Roppongi Hills and cultural landmarks."
    }
]
