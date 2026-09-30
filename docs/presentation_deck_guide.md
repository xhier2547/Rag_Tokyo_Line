# 📊 สไลด์นำเสนอโครงงานตามเกณฑ์ Rubric (Rubric-Aligned Presentation Deck)
## โครงงาน: Tokyo Hybrid Graph RAG for LINE Tourism Assistant

เอกสารฉบับนี้จัดโครงสร้างสไลด์และบทพูดนำเสนอให้ **ตรงตามเกณฑ์การให้คะแนน Rubric ทั้ง 8 ด้าน (Rubric.md)** เพื่อให้อาจารย์และกรรมการตรวจให้คะแนนได้ง่ายที่สุด อธิบายตามลำดับขั้นตอนตั้งแต่การเตรียมข้อมูลไปจนถึงการวัดผลทางวิทยาศาสตร์

---

### Slide 1: หน้าปกโครงงาน (Title Slide)
* **ชื่อโครงงาน:** Tokyo Hybrid Graph RAG: ระบบผู้ช่วยท่องเที่ยวและวางแผนเส้นทางรถไฟโตเกียวบน LINE ด้วยการผสาน Knowledge Graph และ Large Language Model
* **ผู้จัดทำ:** นักศึกษาชั้นปีที่ 4 ภาควิชาวิศวกรรมคอมพิวเตอร์ / วิทยาการคอมพิวเตอร์
* **ใจความสำคัญ (Key Message):** การแก้ปัญหา Hallucination และข้อจำกัดด้านความสัมพันธ์เชิงพื้นที่ของ Vector-only RAG ด้วยการผสาน Neo4j Knowledge Graph เข้ากับ Vector Database อย่างเป็นระบบ

---

### Slide 2: ที่มาและความสำคัญ (Motivation & Problem Statement)
* **ปัญหาของ Traditional Vector-only RAG (ทำไมเวกเตอร์อย่างเดียวถึงไม่พอ?):**
  1. **Spatial & Multi-hop Blindness:** เวกเตอร์ค้นหาคำที่ "ความหมายคล้ายกัน" ได้ดี แต่ตอบคำถามความสัมพันธ์เชิงพื้นที่ไม่ได้ เช่น *"จากสถานี A ไปสถานี B มีสถานที่อะไรระหว่างทางบ้าง?"* เวกเตอร์มักดึงข้อมูลกระจัดกระจายและเกิด Hallucination
  2. **ขาดโครงสร้างความสัมพันธ์ที่แน่นอน (Lack of Deterministic Graph Topology):** ข้อมูลสายรถไฟและการเปลี่ยนสายต้องการความถูกต้อง 100% ซึ่งเวกเตอร์ไม่สามารถการันตีได้
* **แนวทางแก้ไขของโครงงาน:**
  - สร้างสถาปัตยกรรม **Hybrid Graph RAG** ผสาน **ChromaDB (Dense Semantic)** + **Neo4j (Knowledge Graph)** เข้าด้วยกันด้วยกลยุทธ์ **Reciprocal Rank Fusion (RRF)**

---

### Slide 3: [Rubric ด้านที่ 1] Data & Knowledge Base (การเตรียมและจัดโครงสร้างข้อมูล)
*สอดคล้องกับ Rubric 3.1: Data Cleaning, Chunking Strategy, และ Metadata Tagging*
* **1. แหล่งข้อมูล (Data Sources):**
  - ข้อมูลสถานที่ท่องเที่ยวโตเกียว 40+ แห่ง, สถานีรถไฟหลัก 18 สถานี, และเส้นทางรถไฟ 12 สาย
  - มีเอกสารบันทึกที่มาของข้อมูลและการตรวจสอบ Data Provenance ชัดเจนใน `data_sources.md`
* **2. กลยุทธ์การตัดแบ่งข้อมูล (Chunking Strategy):**
  - **ตัวตัดคำ:** `TokyoDocumentChunker` ใช้ Recursive Character Splitting
  - **Chunk Size:** `400` ตัวอักษร (ขนาดพอเหมาะ ไม่สั้นเกินไปจนเสียใจความ และไม่ยาวเกินไปจนเจือจางความหมาย)
  - **Chunk Overlap:** `80` ตัวอักษร (20% Overlap เพื่อรักษาความต่อเนื่องของประโยคข้าม Chunk)
  - **Separators:** `["\n\n", "\n", "。", " ", ""]` (รองรับทั้งภาษาไทย อังกฤษ และภาษาญี่ปุ่น `。`)
* **3. โครงสร้าง Metadata สำหรับกรองข้อมูล (Metadata Schema):**
  - ทุก Chunk แนบ Metadata: `place_id`, `name_th`, `name_en`, `ward`, `category`, `nearest_station_id`, `walk_time_min`

---

### Slide 4: [Rubric ด้านที่ 2] Dense RAG Architecture (การสืบค้นเชิงความหมาย)
*สอดคล้องกับ Rubric 3.2: Embedding, Vector Retrieval, Hyperparameters และการทดสอบโมเดล*
* **1. โครงสร้าง Vector Database:**
  - ใช้ **ChromaDB** สำหรับจัดเก็บ Text Chunks และทำ Similarity Search
  - รองรับ **Metadata Filtering** กรองตามย่าน (`ward`) หรือประเภทสถานที่ (`category`)
* **2. ผลการทดลองเปรียบเทียบโมเดล Embedding (Embedding Benchmark 30 คำถาม):**

| โมเดล (Embedding Model) | มิติ (Dimensions) | เวลาสร้าง Index (Build Time) | Query Latency | Hit@1 | Hit@3 |
|---|:---:|:---:|:---:|:---:|:---:|
| **paraphrase-multilingual-MiniLM-L12-v2** | 384 | 20.32 วินาที | **16.45 ms** | 47% | 67% |
| **multilingual-e5-small** | 384 | **12.41 วินาที** | 18.39 ms | **70%** | **80%** |

* **รูปภาพประกอบ:** [reports/charts/chart_1_embedding_comparison.png](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/reports/charts/chart_1_embedding_comparison.png)
* **ข้อสรุปเชิงวิเคราะห์:** E5-small ให้ความแม่นยำสูงกว่า MiniLM อย่างมีนัยสำคัญ (+13% ถึง +23%) และสร้างดัชนีเร็วกว่าเกือบเท่าตัว

---

### Slide 5: [Rubric ด้านที่ 3] Graph RAG Architecture (ความสัมพันธ์เชิงพื้นที่และเส้นทาง)
*สอดคล้องกับ Rubric 3.3: Knowledge Graph Schema, Multi-hop Traversal, และ Cypher Query*
* **1. โครงสร้าง Graph Schema ใน Neo4j:**
  - **Node Types:** `(:Attraction)`, `(:Station)`, `(:Line)`, `(:District)`
  - **Relationships:**
    - `(:Attraction)-[:NEAR {walk_time_min}]->(:Station)`
    - `(:Station)-[:ON_LINE {seq_order}]->(:Line)`
    - `(:Station)-[:TRANSIT_TO]->(:Station)`
    - `(:Attraction)-[:LOCATED_IN]->(:District)`
* **2. กลไกการสืบค้น (Graph Traversal & Cypher Query):**
  - ค้นหาเส้นทางและความสัมพันธ์แบบ **1-hop และ 2-hop (Multi-hop Query)**
  - สามารถตอบคำถามที่เวกเตอร์ทำไม่ได้ เช่น *"จากสถานี A นั่งรถไฟสาย X ไปสถานี B มีสถานที่ท่องเที่ยวอะไรบ้างที่เดินไม่เกิน 10 นาที"*
* **รูปภาพประกอบ:** [reports/charts/neo4j_graph_overview.png](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/reports/charts/neo4j_graph_overview.png) (ภาพคลัสเตอร์กราฟแสดง Node และ Edge ในระบบ)

---

### Slide 6: [Rubric ด้านที่ 4] Hybrid RAG & Reciprocal Rank Fusion (⭐ หัวใจของโครงงาน)
*สอดคล้องกับ Rubric 3.4: การผสาน Dense + Graph, Fusion Strategy, และ Top-K Hyperparameters*
* **1. สถาปัตยกรรมการสืบค้น 3 ทาง (Three-Way Hybrid Search):**
  - **Dense Retrieval (ChromaDB):** ดึง `Top-K = 15` จากความหมายเชิงลึก
  - **Sparse Lexical Search (BM25):** ดึง `Top-K = 15` จากการจับคู่คีย์เวิร์ดชื่อเฉพาะ
  - **Graph Context (Neo4j):** ดึงเส้นทางและสถานที่ข้างเคียงผ่าน Cypher Traversal
* **2. กลยุทธ์การจัดอันดับ Reciprocal Rank Fusion (RRF):**
  $$RRF\_Score(d) = \sum_{m \in \{Dense, BM25\}} \frac{1}{k + r_m(d)} \quad (k=60)$$
* **3. การคัดเลือกบริบทสุดท้าย (Re-ranking & Top-N Selection):**
  - คัดกรองเหลือชิ้นข้อมูลที่ดีที่สุด **`Top-N = 5`** สำหรับคำถามทั่วไป
  - **Adaptive Dynamic Top-N:** ปรับเป็น **`Top-N = 8`** อัตโนมัติหากตรวจพบคำถามแนวแนะนำหลายสถานที่ (เช่น *"แนะนำ 5 ที่เที่ยว"*, *"มีที่ไหนบ้าง"*)

---

### Slide 7: [Rubric ด้านที่ 5] LLM Integration & Prompt Engineering
*สอดคล้องกับ Rubric 3.5: Multi-backend LLM, Prompt Template, Citations, และ Token Throughput*
* **1. โครงสร้าง Prompt และ Zero-Hallucination Guardrails:**
  - ออกแบบกล่องบริบทแยกชัดเจนระหว่าง `Graph Context` และ `Vector Context`
  - บังคับให้ใส่ป้ายอ้างอิงท้ายชื่อสถานที่เสมอ เช่น `[อ้างอิง: วัดเซ็นโซจิ (สถานีใกล้เคียง: Asakusa)]` หากไม่มีในบริบทห้ามแต่งเติมเอง
* **2. การเปรียบเทียบโมเดลภาษา (Multi-backend Comparison):**

| Backend LLM | สถาปัตยกรรม | Avg. Latency | Throughput | Citation Consistency |
|---|---|:---:|:---:|:---:|
| **Local Qwen 2.5 3B** | Offline Local (Ollama) | **4.566 วินาที** | **195.8 tok/s** | 5 citations / ข้อ |
| **Gemini 3.1 Flash Lite** | Cloud API | 14.322 วินาที | ~15.0 tok/s | 12 citations / ข้อ |
| **Deterministic Fallback** | In-Memory Heuristic Rule | **0.0003 วินาที** | Instant Rule | Heuristic Baseline |

* **รูปภาพประกอบ:** [reports/charts/chart_2_llm_latency_throughput.png](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/reports/charts/chart_2_llm_latency_throughput.png)

---

### Slide 8: [Rubric ด้านที่ 6] System Integration & End-to-End Pipeline
*สอดคล้องกับ Rubric 3.6: Data Flow, Multi-turn Session, และ Fallback Resilience*
* **1. การไหลของข้อมูลแบบ End-to-End:**
  `LINE Message` $\rightarrow$ `FastAPI Webhook` $\rightarrow$ `Intent Router` $\rightarrow$ `Hybrid Retrieval (Chroma+Neo4j)` $\rightarrow$ `RRF Fusion` $\rightarrow$ `LLM Generation` $\rightarrow$ `LINE Flex Message Cards`
* **2. Multi-turn Session Management:**
  - มีโมดูล `SessionManager` จดจำบริบทการสนทนา ตอบคำถามต่อเนื่องได้ เช่น *"จากตรงนั้น เดินไปไหนต่อได้อีก?"*
* **3. Fallback Mechanism (ความคงทนของระบบ):**
  - หาก Neo4j ขัดข้อง $\rightarrow$ Dense Retrieval ยังตอบคำถามทั่วไปได้
  - หาก Cloud API เกิด Timeout หรือ HTTP 503 $\rightarrow$ ระบบสลับไปใช้ Local LLM หรือ Deterministic Fallback ตอบคำถามได้ทันที ไม่เกิด Error หน้าพัง

---

### Slide 9: [Rubric ด้านที่ 7] ผลการทดลอง Retrieval Ablation Study (100 คำถาม)
*สอดคล้องกับ Rubric 3.7: การวัดผลเชิงวิทยาศาสตร์ Hit@1, Hit@3, MRR และการเปรียบเทียบ*
* **ตารางผลการทดลอง 100 คำถามมาตรฐาน:**

| สถาปัตยกรรม (Architecture) | Hit@1 | **Hit@3** | **MRR** | จุดเด่น / ข้อจำกัด |
|---|:---:|:---:|:---:|---|
| **Dense Only (ChromaDB)** | 42.0% | 64.0% | 0.5183 | ดีในคำถามกว้าง แต่ตกม้าตายเรื่องเส้นทาง |
| **Graph Only (Neo4j)** | 53.0% | 54.0% | 0.5358 | แม่นในข้อแรก แต่ขาดความหลากหลายในอันดับถัดไป |
| **Hybrid RAG (RRF Fusion)** | **54.0%** | **74.0%** | **0.6546** | **ดีที่สุดทุกตัวชี้วัด (MRR ชนะ Dense +26.3%)** |

* **รูปภาพประกอบ:** [reports/charts/chart_5_retrieval_ablation.png](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/reports/charts/chart_5_retrieval_ablation.png)
* **บทวิเคราะห์:** พิสูจน์ชัดเจนว่า Hybrid รวมจุดเด่นของ Dense (ความกว้าง) และ Graph (ความแม่นยำเชิงพื้นที่) ทำให้ Hit@3 พุ่งแตะ 74%

---

### Slide 10: [Rubric ด้านที่ 7] ผลการทดลองเจาะลึกแยกตามหมวดหมู่คำถาม (Category A–J)
*สอดคล้องกับ Rubric 3.7: Root-Cause Analysis เจาะลึกว่าทำไมวิธีหนึ่งถึงชนะอีกวิธีในแต่ละคำถาม*

| หมวดหมู่ (Category) | ตัวอย่างคำถาม | Dense Hit@3 | Graph Hit@3 | **Hybrid Hit@3** | พลังของ Knowledge Graph |
|---|---|:---:|:---:|:---:|:---:|
| **B: วัดและประวัติศาสตร์** | ประวัติวัดเซ็นโซจิและการเดินทาง | 70% | 60% | **100%** | **+30%** (ตอบถูกครบ 10/10 ข้อ) |
| **E: อาหารและตลาดปลา** | ร้านอาหารและสตรีทฟู้ดรอบสึกิจิ | 70% | 70% | **90%** | **+20%** |
| **G: การเดินทางและรถไฟ** | นั่งรถไฟจากชินจูกุไปอุเอโนะ | 100% | 80% | **100%** | **MRR 1.000 (แม่นยำสมบูรณ์)** |
| **J: Complex Multi-hop** | แนะนำสถานที่ใกล้สถานี A ที่มีรถไฟไป B | 30% | 60% | **70%** | **+40% (Graph เหนือกว่า Dense เท่าตัว)** |

* **ประเด็นนำเสนอ:** หมวด J เป็นข้อพิสูจน์ทางวิชาการที่ชัดเจนที่สุดว่า Knowledge Graph จำเป็นอย่างยิ่ง เพราะเวกเตอร์เดี่ยวๆ ทำได้เพียง 30%

---

### Slide 11: [Rubric ด้านที่ 7] Systematic Error Analysis (การวิเคราะห์สาเหตุข้อผิดพลาด)
*สอดคล้องกับ Rubric 3.7: การจำแนก Failure Modes จากข้อที่ระบบตอบไม่ติด Top 1*
* **ตารางจำแนกสาเหตุข้อผิดพลาด (Failure Mode Classification จาก 100 ข้อ):**

| สาเหตุความผิดพลาด (Failure Mode) | สัดส่วน (%) | จำนวนข้อ | คำอธิบายและแนวทางแก้ไข |
|---|:---:|:---:|---|
| **1. Unstructured Semantic Gap** | **37.0%** | 17 ข้อ | คำถามกว้างเชิงคุณภาพ (เช่น *"ที่เที่ยวครึ่งวัน"*) $\rightarrow$ เติม Cross-Encoder Re-ranker |
| **2. Graph Coverage Gap** | **34.8%** | 16 ข้อ | กราฟยังขาดข้อมูลสถานีย่อยบางจุด $\rightarrow$ เพิ่ม Ingestion เส้นทางรถไฟเพิ่มเติม |
| **3. Fusion Weight Imbalance** | **28.3%** | 13 ข้อ | RRF ให้คะแนนสัญญาณหลอกแย่งอันดับ $\rightarrow$ ใช้ Dynamic Confidence-Weighted RRF |
| **4. Entity Extraction Failure** | **0.0%** | 0 ข้อ | สกัดคำภาษาไทยได้สมบูรณ์ ไม่พลาดชื่อเฉพาะ |

* **รูปภาพประกอบ:** [reports/charts/chart_6_error_distribution.png](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/reports/charts/chart_6_error_distribution.png)

---

### Slide 12: [Rubric ด้านที่ 7 & 8] Human Evaluation Protocol & Live Demonstration
*สอดคล้องกับ Rubric 3.7 (Human Evaluation) และ 3.8 (Documentation & Demo)*
* **1. กรอบการประเมินโดยมนุษย์ (Double-Blind Protocol):**
  - ประเมิน 4 มิติ (1–5 คะแนน): **Faithfulness**, **Answer Relevance**, **Grounding & Citation**, และ **Linguistic Fluency**
  - วัดความสอดคล้องของผู้ตรวจด้วย **Cohen's Kappa ($\kappa > 0.60$)**
* **2. การแสดงผลจริงบน LINE Bot (Live Demo Showcase):**
  - แสดง **Flex Message Media Cards:** รูปภาพสถานที่จริง, เวลาเปิด-ปิด, สถานีใกล้เคียง
  - **Interactive Button:** ปุ่มกดเปิด Google Maps นำทางได้ทันที
* **3. บทสรุปโครงงาน:**
  - สถาปัตยกรรม Hybrid Graph RAG บรรลุผลตามเกณฑ์ Rubric Level 5 ในหัวข้อหลัก
  - พิสูจน์ด้วยตัวเลขเชิงประจักษ์ 100 ข้อสอบ ว่าตอบโจทย์การเดินทางได้เหนือกว่า Traditional RAG อย่างแท้จริง
