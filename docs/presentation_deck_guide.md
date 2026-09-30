# 📊 คู่มือนำเสนอโครงงาน (Presentation Deck Guide)
## โครงงาน: Tokyo Hybrid Graph RAG for LINE Tourism Assistant

เอกสารฉบับนี้ถูกออกแบบมาเพื่อใช้เป็นโครงสร้างสไลด์และบทพูดนำเสนอ (Slide-by-Slide Presentation) โดยเน้น **ผลลัพธ์เชิงประจักษ์ (Empirical Results), ตารางตัวเลขสถิติ, กราฟเปรียบเทียบ (300 DPI), และการวิเคราะห์ทางวิศวกรรม**

---

### Slide 1: หน้าปกโครงงาน (Title Slide)
* **หัวข้อ:** Tokyo Hybrid Graph RAG: Intelligent LINE Tourism Assistant with Multi-hop Knowledge Graph & Local-Cloud LLM Fusion
* **ผู้จัดทำ / สาขา:** นักศึกษาชั้นปีที่ 4 ภาควิชาวิศวกรรมคอมพิวเตอร์ / โครงงานวิทยาการคอมพิวเตอร์
* **ประเด็นเปิดนำ:** ระบบแนะนำการท่องเที่ยวและเส้นทางรถไฟในโตเกียวที่แก้ปัญหา Hallucination และข้อจำกัดด้านความสัมพันธ์เชิงพื้นที่ของ Traditional RAG ด้วยการผสาน Neo4j Knowledge Graph เข้ากับ Vector Database

---

### Slide 2: ที่มาและความสำคัญ (Motivation & Problem Statement)
* **ปัญหาของ Traditional Vector-only RAG:**
  1. **Spatial & Multi-hop Blindness:** เวกเตอร์ค้นหาข้อความที่ "ความหมายใกล้กัน" ได้ดี แต่ตอบคำถามความสัมพันธ์เชิงพื้นที่ไม่ได้ เช่น *"จากชินจูกุ นั่งรถไฟสายไหนไปวัดเซ็นโซจิ และระหว่างทางผ่านสถานีอะไรบ้าง?"* เวกเตอร์มักคืนข้อมูลกระจัดกระจายและเกิด Hallucination
  2. **ความเสี่ยงของ Cloud API:** Latency ไม่แน่นอน เสียค่าใช้จ่าย และมีปัญหา Rate Limit / HTTP 503
* **ทางออกของโครงงาน:**
  - สร้าง **Hybrid Retrieval Engine** ผสาน ChromaDB (Dense) + Neo4j (Knowledge Graph) ด้วยสูตร **Reciprocal Rank Fusion (RRF)**
  - รองรับ **Multi-backend LLM**: Gemini 3.1 Flash Lite (Cloud) คู่ขนานกับ Qwen 2.5 3B (Local Offline) พร้อมระบบ Fallback

---

### Slide 3: สถาปัตยกรรมระบบ (System Architecture & Pipeline)
* **ภาพรวม Pipeline:**
  1. **Data Ingestion:** แปลงข้อมูล Markdown $\rightarrow$ Knowledge Graph (18 สถานีหลัก, 40+ สถานที่ท่องเที่ยว, 12 เส้นทางรถไฟ) + ChromaDB (Chunsize 500)
  2. **Hybrid Retrieval:** ดึง Context ผ่าน Dense Semantic Search + Cypher Multi-hop Graph Traversal $\rightarrow$ จัดอันดับด้วย RRF ($k=60$)
  3. **Generation Layer:** Prompt บังคับ Grounding & Citations $\rightarrow$ สร้างคำตอบภาษาไทย
  4. **Presentation Layer:** ส่งออกผ่าน LINE Webhook $\rightarrow$ Flex Message & Carousel Cards
* **รูปภาพประกอบสไลด์:**
  - [reports/charts/neo4j_graph_overview.png](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/reports/charts/neo4j_graph_overview.png) (โครงสร้างกราฟและคลัสเตอร์ความสัมพันธ์ในโตเกียว)

---

### Slide 4: ผลการทดลองที่ 1 - Retrieval Ablation Study (100 คำถาม)
* **ตารางเปรียบเทียบประสิทธิภาพ Retrieval (100 Test Queries):**

| สถาปัตยกรรม (Architecture) | Hit@1 | **Hit@3** | **MRR** | Graph Coverage | Retrieval Latency |
|---|:---:|:---:|:---:|:---:|:---:|
| **Dense Only (ChromaDB)** | 42.0% | 64.0% | 0.5183 | 0% | 15.08 ms |
| **Graph Only (Neo4j)** | 53.0% | 54.0% | 0.5358 | 80% | **0.16 ms** |
| **Hybrid RAG (RRF Fusion)** | **54.0%** | **74.0%** | **0.6546** | **80%** | 27.36 ms |

* **รูปภาพประกอบสไลด์:**
  - [reports/charts/chart_5_retrieval_ablation.png](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/reports/charts/chart_5_retrieval_ablation.png)
* **ประเด็นพูดนำเสนอ:**
  - *"ผลการทดลอง 100 ข้อพิสูจน์ชัดเจนว่า Hybrid RAG ให้ค่า Hit@3 สูงถึง 74% และเพิ่มค่า MRR ขึ้นจาก Dense Only ถึง 26.3% (0.5183 ➔ 0.6546)"*
  - *"แม้ Hybrid จะใช้เวลาเพิ่มขึ้นเล็กน้อย (+12 ms จากการรวม 2 Engine) แต่แลกมาด้วยความแม่นยำของข้อมูลที่เพิ่มขึ้นอย่างมีนัยสำคัญ"*

---

### Slide 5: ผลการทดลองที่ 2 - เจาะลึกรายหมวดหมู่ (Category-Wise Breakdown A ถึง J)
* **ตารางผลลัพธ์แยกตามประเภทคำถาม:**

| หมวดหมู่ (Category) | ตัวอย่างคำถาม | Dense Hit@3 | Graph Hit@3 | **Hybrid Hit@3** | ประโยชน์ของ Graph |
|---|---|:---:|:---:|:---:|:---:|
| **B: วัดและประวัติศาสตร์** | ประวัติวัดเซ็นโซจิและการเดินทาง | 70% | 60% | **100%** | **+30%** |
| **E: อาหารและย่านกินเที่ยว** | สตรีทฟู้ดและตลาดปลา | 70% | 70% | **90%** | **+20%** |
| **G: การเดินทางและรถไฟ** | นั่งรถไฟจากชินจูกุไปอุเอโนะ | 100% | 80% | **100%** | **MRR 1.000** |
| **J: Complex Multi-hop Graph** | สถานที่ใกล้สถานี A ที่มีรถไฟต่อไป B | 30% | 60% | **70%** | **+40% (ก้าวกระโดด)** |

* **ประเด็นพูดนำเสนอ:**
  - *"ในหมวด J ซึ่งเป็นคำถามเชื่อมโยงหลายทอด (Multi-hop) Dense ทำได้เพียง 30% แต่เมื่อมี Knowledge Graph ดันคะแนนขึ้นเป็น 70% แสดงให้เห็นว่าเวกเตอร์อย่างเดียวไม่สามารถตอบโจทย์การเดินทางได้"*

---

### Slide 6: ผลการทดลองที่ 3 - การเปรียบเทียบโมเดล Embedding
* **ตารางเปรียบเทียบโมเดลตัดคำและเวกเตอร์ (30 คำถาม):**

| โมเดล (Embedding Model) | มิติ (Dimensions) | เวลาสร้าง Index (Build Time) | Query Latency | Hit@1 | Hit@3 |
|---|:---:|:---:|:---:|:---:|:---:|
| **MiniLM-L12-v2** | 384 | 20.32 วินาที | **16.45 ms** | 47% | 67% |
| **Multilingual-E5-Small** | 384 | **12.41 วินาที** | 18.39 ms | **70%** | **80%** |

* **รูปภาพประกอบสไลด์:**
  - [reports/charts/chart_1_embedding_comparison.png](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/reports/charts/chart_1_embedding_comparison.png)
* **ประเด็นพูดนำเสนอ:**
  - *"E5-small ให้ความแม่นยำสูงกว่า MiniLM ถึง 13–23 จุดเปอร์เซ็นต์ และสร้าง Index เร็วกว่าเกือบเท่าตัว แม้ Latency ตอนค้นหาจะช้ากว่าเพียง 1.9 ms"*

---

### Slide 7: ผลการทดลองที่ 4 - การเปรียบเทียบ LLM Backends (Cloud vs Local)
* **ตารางเปรียบเทียบ Generation Latency และ Throughput (10 ข้อมาตรฐาน):**

| Backend | ประเภท | Avg. Latency | Throughput | Citation Count | ค่าใช้จ่าย (Cost) |
|---|---|:---:|:---:|:---:|:---:|
| **Local Qwen 2.5 3B** | Local Offline (Ollama) | **4.566 วินาที** | **195.8 tokens/s** | 5 citations / query | **0 บาท (ฟรี)** |
| **Gemini 3.1 Flash Lite** | Cloud API | 14.322 วินาที | ~15.0 tokens/s | 12 citations / query | ตามการใช้งาน API |
| **Deterministic Fallback** | Local In-Memory Rule | **0.0003 วินาที** | Instant Rule | 0 (Heuristic) | **0 บาท** |

* **รูปภาพประกอบสไลด์:**
  - [reports/charts/chart_2_llm_latency_throughput.png](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/reports/charts/chart_2_llm_latency_throughput.png)
  - [reports/charts/chart_4_category_latency.png](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/reports/charts/chart_4_category_latency.png)
* **ประเด็นพูดนำเสนอ:**
  - *"Qwen 2.5 3B ที่รันแบบ Local ให้ความเร็วสูงถึง 195.8 tokens/s และ Latency เพียง 4.56 วินาที เร็วกว่า Cloud API ที่บางครั้งติดคอขวดเน็ตเวิร์กและการ Retry HTTP 503"*

---

### Slide 8: ผลการทดลองที่ 5 - การวัดผลฮาร์ดแวร์จริงและความปลอดภัยของระบบ (Resource Profiling)
* **ตารางตรวจวัดบนเครื่องจริง (NVIDIA GeForce RTX 3080 Ti 12GB):**

| ตัวชี้วัดฮาร์ดแวร์ (Hardware Metric) | ค่าที่วัดได้จริง | ขีดจำกัดฮาร์ดแวร์ | สถานะความปลอดภัย |
|---|:---:|:---:|:---:|
| **Peak GPU VRAM** | **1,920 MB** | 12,288 MB (12 GB) | ปลอดภัยมาก (ใช้เพียง 15.6%) |
| **GPU Utilization Peak** | **34.2%** | 100% | มี Headroom เหลือเฟือ |
| **System RAM Peak** | **11,450 MB (+648 MB RSS)** | 24,576 MB (24 GB) | กิน RAM เพิ่มเล็กน้อย |
| **Average CPU Load** | **14.8% (Peak 22.4%)** | 100% | ไม่กระทบต่อ OS และ LINE Server |
| **SSD Active Time / Write** | **0.0 MB/s (Read) / 0.12 MB/s** | Unlimited | **Zero Thrashing (ไม่แตะ Swap SSD)** |

* **รูปภาพประกอบสไลด์:**
  - [reports/charts/chart_3_llm_resource_usage.png](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/reports/charts/chart_3_llm_resource_usage.png)
* **ประเด็นพูดนำเสนอ:**
  - *"เราออกแบบระบบ Hardware Profiler พร้อม SSD Circuit Breaker โดยพิสูจน์ว่าโมเดล 3B ถูกโหลดเข้าสู่ VRAM 100% ทำให้ไม่เกิด Disk Paging หรือ SSD พุ่ง 100% ป้องกันปัญหาเครื่องร้อนหรือดับได้อย่างสมบูรณ์แบบ"*

---

### Slide 9: การวิเคราะห์ข้อผิดพลาดเชิงลึก (Systematic Error Analysis)
* **การจำแนกสาเหตุข้อผิดพลาด (Failure Mode Distribution จาก 100 คำถาม):**

| สาเหตุความผิดพลาด (Failure Mode) | สัดส่วน (%) | จำนวนข้อ | คำอธิบายและแนวทางแก้ปัญหาเชิงสถาปัตยกรรม |
|---|:---:|:---:|---|
| **1. Unstructured Semantic Gap** | **37.0%** | 17 ข้อ | คำถามกว้างเชิงนามธรรม (เช่น *"ที่เที่ยวครึ่งวัน"*) $\rightarrow$ เติม Cross-Encoder Semantic Re-ranker |
| **2. Graph Coverage Gap** | **34.8%** | 16 ข้อ | กราฟยังขาดเส้นทางเชื่อมโยงย่อย $\rightarrow$ เพิ่ม Schema และ Ingest เส้นทางรถบัส/สถานีย่อย |
| **3. Fusion Weight Imbalance** | **28.3%** | 13 ข้อ | RRF ดึงผลลัพธ์หลอกเข้ามาแย่งอันดับ $\rightarrow$ ใช้ Dynamic Confidence-Weighted RRF |
| **4. Entity Extraction Failure** | **0.0%** | 0 ข้อ | การตัดคำภาษาไทยทำงานได้สมบูรณ์ ไม่พลาดชื่อสถานที่ |

* **รูปภาพประกอบสไลด์:**
  - [reports/charts/chart_6_error_distribution.png](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/reports/charts/chart_6_error_distribution.png)

---

### Slide 10: ระเบียบวิธีการประเมินโดยมนุษย์ (Human Evaluation Framework)
* **กรอบการประเมินแบบ Double-Blind (1–5 คะแนน):**
  1. **Faithfulness (1–5):** ความซื่อตรงต่อบริบท ปราศจากการแต่งข้อมูล (Zero Hallucination)
  2. **Answer Relevance (1–5):** ตอบตรงคำถาม ตรงจุด ไม่เวิ่นเว้อ
  3. **Grounding & Citation (1–5):** ความถูกต้องของการระบุป้าย `[อ้างอิง: ...]`
  4. **Linguistic Fluency (1–5):** ภาษาไทยสละสลวย เป็นธรรมชาติ
* **เกณฑ์ความน่าเชื่อถือทางสถิติ:**
  - ใช้วัดความสอดคล้องระหว่างผู้ตรวจด้วย **Cohen's Kappa ($\kappa > 0.60$)** รับรองความเที่ยงตรงทางวิชาการ

---

### Slide 11: การแสดงผลบน LINE Application จริง (Live Showcase)
* **ฟีเจอร์เด่นของ LINE Bot:**
  - **Flex Message Media Cards:** แสดงรูปภาพสถานที่จริง, เวลาเปิด-ปิด, สถานีใกล้เคียง
  - **Interactive Buttons:** ปุ่มกดเปิด Google Maps นำทางได้ทันที
  - **Multi-turn Session:** จดจำประวัติการสนทนา ตอบคำถามต่อเนื่อง เช่น *"จากที่นั่น นั่งรถไฟไปไหนต่อได้อีก?"*

---

### Slide 12: บทสรุปและคุณค่าของโครงงาน (Conclusion & Value Proposition)
1. **แก้ปัญหา RAG เดิมได้อย่างเด็ดขาด:** Hybrid Graph RAG เพิ่ม Hit@3 เป็น 74% และ MRR 0.6546 โดยเฉพาะโจทย์ Multi-hop ที่ดีกว่าเวกเตอร์ถึง 40%
2. **เสถียรภาพและประสิทธิภาพฮาร์ดแวร์:** รันได้ทั้ง Cloud และ Local LLM (3B) กิน VRAM เพียง 1.9 GB โดยไม่มีปัญหา SSD Overload
3. **ความสมบูรณ์เชิงวิชาการ:** มีผลทดลองเปรียบเทียบครบทั้ง Retrieval, Embedding, LLM, Hardware และ Error Analysis อย่างเป็นวิทยาศาสตร์
