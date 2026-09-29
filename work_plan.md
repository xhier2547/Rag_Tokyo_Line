# Implementation & System Architecture Plan: Tokyo Smart Transit & Tourism Hybrid Graph RAG

**เป้าหมายของระบบ:** พัฒนาระบบแนะนำเส้นทาง สถานที่ท่องเที่ยว และการเดินทางในกรุงโตเกียว (Tokyo) โดยบูรณาการ **Dense RAG (FAISS/ChromaDB)**, **Sparse Search (BM25)**, **Knowledge Graph (Neo4j)**, **Local LLM (Ollama 3B/4B/8B)** และ **API LLM (Gemini API)** มุ่งสู่ระดับคุณภาพสูงสุด **Level 5 (Advanced / Excellent)** ตามเกณฑ์ใน [rubic.md](file:///c:/Users/wator/Documents/Y4/SOCIAL/Final_01/rubic.md)

---

## 1. การวิเคราะห์ไฟล์ที่มีอยู่และการประเมินความเสี่ยง (Risk Assessment)

### ไฟล์เดิมใน Workspace
- `rubic.md`: ไฟล์เกณฑ์การประเมิน (Source of Truth) — *คงเดิม ไม่มีการแก้ไข*
- `.git/`: Version control repository — *ใช้บันทึกประวัติการพัฒนาและเป็นจุด Rollback*

### การประเมินความเสี่ยงและแนวทางป้องกัน (Risks & Mitigations)
1. **ความเสี่ยงด้านปริมาณและขนาดข้อมูล (Dataset Volume Risk):** ข้อมูล OSM Japan ทั้งประเทศมีขนาดใหญ่ (หลาย GB)
   - *แนวทางป้องกัน:* กรองเฉพาะเขตกรุงโตเกียว (Tokyo Metropolitan Area / 23 Wards) และมุ่งเน้นเส้นทางรถไฟหลัก (JR Yamanote, Tokyo Metro, Toei Subway) ผสานกับ POI จาก JTA Sightseeing Database
2. **ความเสี่ยงด้านการเชื่อมต่อ Neo4j (Database Availability Risk):** กรณีเครื่องที่รันไม่มี Neo4j Service หรือยังไม่ได้เริ่มรัน Docker
   - *แนวทางป้องกัน:* ออกแบบระบบให้มี **Local JSON / NetworkX Graph Fallback Mechanism** แบบเดียวกับโปรเจกต์เดิม เพื่อให้ระบบและ Automated Test ทำงานได้อย่างต่อเนื่องไม่สะดุด
3. **ความเสี่ยงด้านหน่วยความจำ (Hardware Memory & VRAM Contention):** การรันทั้ง Embedding Model และ Local LLM บน GPU อาจทำให้เกิด Out of Memory (OOM)
   - *แนวทางป้องกัน:* ตั้งค่า Embedding Model ให้รันบน CPU หรือใช้โมเดลขนาดเล็ก เช่น `bge-m3` (quantized) / `multilingual-e5-small` และใช้โมเดล Ollama ขนาดกะทัดรัด (3B–4B)
4. **ความเสี่ยงด้าน Hallucination ในการบอกเส้นทาง:** LLM อาจจินตนาการสถานีหรือเวลาเดินทางเอง
   - *แนวทางป้องกัน:* กำหนด Zero-Hallucination Guardrail โดยให้ข้อมูลเส้นทางและเวลาเดินทางมาจาก Neo4j Graph Query เท่านั้น และบังคับใส่ Tag อ้างอิงแหล่งข้อมูล `[อ้างอิง: ...]`

---

## 2. ลำดับขั้นตอนการพัฒนา (Phase-by-Phase Roadmap)

### Phase 1: การเตรียมข้อมูลและสร้าง Knowledge Base (Data & Knowledge Base - 10 คะแนน)
- [ ] **1.1 Data Scraping & Extraction:**
  - สกัดข้อมูลสถานที่ท่องเที่ยวโตเกียวจาก JTA Sightseeing Database (หมวดโตเกียว เช่น วัด, ศาลเจ้า, พิพิธภัณฑ์, ย่านช้อปปิ้ง, สวนสาธารณะ)
  - สกัดข้อมูลสถานีรถไฟโตเกียวและสายรถไฟจาก 駅データ.jp และ OpenStreetMap (JR Yamanote Line, Ginza Line, Marunouchi Line, Shinjuku Line ฯลฯ) พร้อมพิกัด (lat, lon)
- [ ] **1.2 Data Cleaning & Chunking:**
  - ทำความสะอาดข้อความภาษาไทย/อังกฤษ/ญี่ปุ่น ขจัดอักขระแปลกปลอม
  - ใช้ `RecursiveCharacterTextSplitter` โดยกำหนด Boundary และคำเชื่อมที่เหมาะสม
  - กำหนด Metadata ละเอียด: `place_name`, `station_nearby`, `line`, `category`, `ward`, `travel_time_min`, `source`
- [ ] **1.3 Export Clean Datasets:**
  - สร้างไฟล์ structured CSV: `places.csv`, `stations.csv`, `lines.csv`, `routes_edges.csv` และ `documents_chunks.json`

### Phase 2: การสร้าง Graph Database & Cypher Retrieval (Graph RAG - 15 คะแนน)
- [ ] **2.1 Schema Design บน Neo4j:**
  - Nodes: `(:Place)`, `(:Station)`, `(:Line)`, `(:Ward)`, `(:Category)`
  - Relationships:
    - `(:Place)-[:NEAR_STATION {walk_min: Int, distance_m: Int}]->(:Station)`
    - `(:Station)-[:CONNECTED_TO {duration_min: Int, line_name: String}]->(:Station)`
    - `(:Station)-[:ON_LINE]->(:Line)`
    - `(:Place)-[:LOCATED_IN]->(:Ward)`
    - `(:Place)-[:HAS_CATEGORY]->(:Category)`
- [ ] **2.2 Graph Ingestion Script (`build_graph.py`):**
  - เขียนสคริปต์เชื่อมต่อและ Load ข้อมูลเข้า Neo4j แบบ idempotent (`MERGE`)
  - สร้าง JSON Fallback Cache สำหรับออฟไลน์
- [ ] **2.3 Graph Traversal & Cypher Query Engine (`graph_search.py`):**
  - ฟังก์ชันคำนวณเส้นทางสั้นที่สุด (Shortest Path / Travel Duration)
  - ฟังก์ชันค้นหาสถานที่ใกล้สถานี หรือสถานที่ในย่านเดียวกัน

### Phase 3: การสร้าง Vector & Sparse Indices (Dense RAG & Hybrid RAG - 35 คะแนน)
- [ ] **3.1 Vector Database Comparison (ChromaDB vs FAISS):**
  - สร้าง FAISS Index สำหรับข้อความคำอธิบายยาว (Semantic Search)
  - สร้าง ChromaDB Collection พร้อม Metadata Filtering (Category, Ward)
  - ทำการทดสอบเปรียบเทียบ Latency และความแม่นยำ
- [ ] **3.2 Embedding Model Benchmark:**
  - เตรียมสคริปต์เปรียบเทียบโมเดล: `BAAI/bge-m3`, `intfloat/multilingual-e5-base`, `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- [ ] **3.3 Sparse BM25 Index:**
  - สร้าง BM25 Tokenizer ด้วย PyThaiNLP / N-gram สำหรับรองรับคำค้นหาภาษาไทยและชื่อเฉพาะภาษาอังกฤษ/ญี่ปุ่น
- [ ] **3.4 Advanced Hybrid Fusion Engine (`hybrid_engine.py`):**
  - **Query Intent Router:** จำแนกประเภทคำถาม (1. คำถามเส้นทาง/การเดินทาง $\rightarrow$ Graph, 2. คำถามประวัติ/รายละเอียด $\rightarrow$ Vector+BM25, 3. คำถามผสม $\rightarrow$ Hybrid Full)
  - **Reciprocal Rank Fusion (RRF):** คำนวณคะแนนถ่วงน้ำหนักจาก Dense และ Sparse
  - **Cross-Encoder / Semantic Re-ranking:** คัดกรอง Chunks ที่เกี่ยวข้องที่สุด Top-3

### Phase 4: การเชื่อมต่อ Local LLM & API LLM (Local + API LLM - 15 คะแนน)
- [ ] **4.1 Local LLM via Ollama (`local_llm.py`):**
  - รองรับโมเดลขนาด 3B–8B (เช่น `llama3.2:3b`, `qwen2.5:3b`, `typhoon2:8b`)
  - ออกแบบ Dynamic Prompting ที่ปรับ Context Window ให้กระชับ ประหยัดเวลา Generate
- [ ] **4.2 API LLM via Google Gemini (`gemini_llm.py`):**
  - เชื่อมต่อ `google-genai` / LangChain Google GenAI ผ่าน `.env` API Key
  - จัดการ Token Budget, Error Handling, Fallback เมื่อ API เกิด Rate Limit
- [ ] **4.3 Comparative LLM Wrapper:**
  - สวิตช์สลับโมเดลได้ทันทีระหว่างรันเพื่อเปรียบเทียบผลลัพธ์คำตอบแบบ Side-by-Side

### Phase 5: System Integration & Error Handling (System Integration - 10 คะแนน)
- [ ] **5.1 End-to-End Orchestrator (`rag_service.py`):**
  - Workflow: User Query $\rightarrow$ Query Normalization & Synonym Expansion $\rightarrow$ Routing $\rightarrow$ Multi-retrieval $\rightarrow$ Context Assembly $\rightarrow$ LLM $\rightarrow$ Answer with Citations
  - Traceable Citations: ระบุชื่อสถานที่ สถานี หรือแหล่งอ้างอิงจริง
  - Response Caching สำหรับคำถามซ้ำ
- [ ] **5.2 Application Interface:**
  - Interactive CLI พร้อมโหมดเปรียบเทียบ (Compare Mode)
  - *(Optional)* Web UI แบบง่าย (Streamlit) สำหรับนำเสนอ Demo

### Phase 6: การประเมินผลและการวิเคราะห์เชิงลึก (Evaluation & Analysis - 10 คะแนน)
- [ ] **6.1 Benchmark Dataset (`benchmark_qa.json`):**
  - สร้างชุดคำถาม-คำตอบอ้างอิง (Ground Truth) ครอบคลุม:
    - หมวด 1: เส้นทางและการเดินทาง (Route & Station Transit)
    - หมวด 2: สถานที่ท่องเที่ยวและกิจกรรม (Attractions & Activities)
    - หมวด 3: การวางแผนข้ามย่าน (Multi-hop District Itinerary)
- [ ] **6.2 Automated Evaluator (`evaluate.py`):**
  - วัด Retrieval Metrics: Hit@K, MRR (Mean Reciprocal Rank)
  - วัด Generation Metrics: Faithfulness, Answer Relevance
  - วัด System Performance: Latency (sec), RAM/VRAM Usage, Token Usage
- [ ] **6.3 Comprehensive Report Generation:**
  - สร้างรายงานสรุปผลการทดลองเปรียบเทียบเป็นตารางและกราฟิกใน `evaluation_report.md` เพื่อใช้ส่งตรวจรับคะแนน Level 5

### Phase 7: Automated Testing & Documentation (5 คะแนน)
- [ ] เขียน Unit Tests และ Integration Tests ด้วย `pytest` ทดสอบทุกโมดูล
- [ ] จัดทำเอกสารคู่มือ `README.md` และ Architecture Diagram

---

## 3. สรุปความเชื่อมโยงกับเกณฑ์ Rubric Level 5

| ข้อกำหนด Rubric Level 5 | การออกแบบในสถาปัตยกรรมนี้ |
| :---| :---|
| **1. Data & Knowledge Base** | ข้อมูลโตเกียวผ่าน Data Cleaning, Metadata สมบูรณ์, โครงสร้างแยกชัดสำหรับ Vector และ Graph |
| **2. Dense RAG** | ปรับ Top-K, Similarity Threshold, Reranking และมีผลการทดลองเปรียบเทียบหลาย Embedding |
| **3. Graph RAG** | ใช้ Graph ตอบเรื่อง Route & Transit เชื่อมโยง Station $\leftrightarrow$ Place พร้อมพิสูจน์จุดเด่นที่ Dense ทำไม่ได้ |
| **4. Hybrid RAG** | ผสาน Dense + Sparse + Graph ด้วย RRF, Intent Routing และ Semantic Reranking ชัดเจน |
| **5. Local + API LLM** | เปรียบเทียบ Ollama (3B/4B/8B) และ Gemini API พร้อมวัด Latency, Resource และ Output Quality |
| **6. System Integration** | Pipeline สมบูรณ์ มี Caching, Error Handling, Fallback และ Traceable Citations |
| **7. Evaluation & Analysis** | มี Test Benchmark ครอบคลุม วิเคราะห์เปรียบเทียบทุก Configuration อย่างเป็นวิทยาศาสตร์ |
| **8. Documentation** | มี `rubic.md`, `work_plan.md`, `README.md`, โค้ดมีคอมเมนต์ภาษาไทย และ Automated Tests ครบถ้วน |
