# Rubric เกณฑ์การประเมินคุณภาพ Final Project (RAG System)

เอกสารเกณฑ์ระดับคุณภาพ (Rubric) สำหรับใช้ประเมิน Final Project ด้านการพัฒนาระบบ Retrieval-Augmented Generation (RAG) ตั้งแต่ระดับพื้นฐานไปจนถึงขั้นสูง โดยครอบคลุมทั้ง Dense Retrieval, Graph RAG, Hybrid RAG, Local LLM และ API LLM อย่างเป็นระบบ

---

## 1. ปรัชญาและหลักการสำคัญในการประเมิน

> **"การมี Technology ไม่เท่ากับการได้ระดับคุณภาพสูง"**

การพิจารณาคะแนนไม่ได้ตัดสินเพียงแค่ว่า *“มี Technology ติดตั้งอยู่ในโปรเจกต์หรือไม่”* แต่จะพิจารณาจาก:
- **คุณภาพของการนำไปใช้งานจริง** (Real-world applicability & correctness)
- **ความถูกต้องของการออกแบบสถาปัตยกรรม** (Architectural design)
- **การบูรณาการระบบเข้าด้วยกัน** (Integration)
- **ประสิทธิภาพของระบบ** (Performance, latency, cost & resource usage)
- **ความสามารถในการทดลอง วัดผล และวิเคราะห์เชิงลึก** (Experimental analysis & evaluation metrics)

### ตัวอย่างความเข้าใจที่ถูกต้อง
- มี Neo4j $\neq$ Graph RAG อยู่ในระดับสูง
- มี Vector Database $\neq$ Dense RAG มีคุณภาพสูง
- เรียก OpenAI API ได้ $\neq$ API LLM Integration อยู่ในระดับสูง
- มีทั้ง Vector + Graph $\neq$ เป็น Hybrid RAG ระดับสูง
- **ระดับคุณภาพตัดสินจาก:** *“สามารถนำเทคโนโลยีมาแก้ปัญหาได้จริง และสามารถแสดงหลักฐานเชิงประจักษ์จากการทดลองได้ว่าระบบทำงานอย่างมีประสิทธิภาพเพียงใด”*

---

## 2. ตารางคะแนนและสัดส่วนคะแนน (Total: 100 คะแนน)

| ลำดับ | ด้านการประเมิน (Evaluation Dimensions) | คะแนนเต็ม | เกณฑ์คะแนนตามระดับ Level (1–5) |
| :---: | :---| :---: | :---|
| 1 | **Data & Knowledge Base** | 10 | L5: 9–10 \| L4: 7–8 \| L3: 5–6 \| L2: 3–4 \| L1: 0–2 |
| 2 | **Dense RAG** | 15 | L5: 13–15 \| L4: 10–12 \| L3: 7–9 \| L2: 4–6 \| L1: 0–3 |
| 3 | **Graph RAG** | 15 | L5: 13–15 \| L4: 10–12 \| L3: 7–9 \| L2: 4–6 \| L1: 0–3 |
| 4 | **Hybrid RAG** *(หัวใจสำคัญ)* | 20 | L5: 17–20 \| L4: 13–16 \| L3: 9–12 \| L2: 5–8 \| L1: 0–4 |
| 5 | **Local LLM + API LLM** | 15 | L5: 13–15 \| L4: 10–12 \| L3: 7–9 \| L2: 4–6 \| L1: 0–3 |
| 6 | **System Integration** | 10 | L5: 9–10 \| L4: 7–8 \| L3: 5–6 \| L2: 3–4 \| L1: 0–2 |
| 7 | **Evaluation & Analysis** | 10 | L5: 9–10 \| L4: 7–8 \| L3: 5–6 \| L2: 3–4 \| L1: 0–2 |
| 8 | **Documentation / Presentation** | 5 | L5: 5 \| L4: 4 \| L3: 3 \| L2: 2 \| L1: 0–1 |
| **รวม** | **คะแนนรวมทั้งหมด** | **100** | **คำนวณตามผลรวมระดับคะแนนแต่ละด้าน** |

---

## 3. เกณฑ์การประเมินรายด้านอย่างละเอียด (Rubric Details)

### 3.1 Data & Knowledge Base (10 คะแนน)
*การเตรียมและจัดโครงสร้างข้อมูลสำหรับ Vector Database และ Knowledge Graph*
- **Level 5 (9–10 คะแนน):** มีการออกแบบ Dataset และ Knowledge Base อย่างเป็นระบบ มี Data Cleaning, Chunking Strategy ที่ชัดเจน, Metadata ครบถ้วน และการเตรียมข้อมูลสำหรับทั้ง Vector และ Graph อย่างเหมาะสม สามารถอธิบายเหตุผลของการออกแบบเชิงลึกได้ และข้อมูลมีคุณภาพสูงเพียงพอสำหรับการทดลอง
- **Level 4 (7–8 คะแนน):** เตรียมข้อมูลสำหรับ Vector และ Graph ได้ครบถ้วน มีการจัดโครงสร้างและทำความสะอาดข้อมูลเหมาะสม แต่ยังขาดการปรับปรุงหรือวิเคราะห์ข้อมูลเชิงลึกในบางจุด
- **Level 3 (5–6 คะแนน):** มี Dataset และสามารถนำไปสร้าง Vector และ Graph ได้ แต่กระบวนการเตรียมข้อมูลยังเป็นแบบพื้นฐาน (Default settings)
- **Level 2 (3–4 คะแนน):** มี Dataset แต่การเตรียมข้อมูลยังไม่สมบูรณ์ หรือพบปัญหาเรื่อง Chunking, Metadata ขาดหาย หรือโครงสร้าง Graph ไม่เหมาะสม
- **Level 1 (0–2 คะแนน):** มีข้อมูลทดลองเพียงเล็กน้อย (Toy dataset) หรือไม่สามารถอธิบายกระบวนการและที่มาของการเตรียมข้อมูลได้

---

### 3.2 Dense RAG (15 คะแนน)
*กระบวนการ Vector Embedding, Retrieval และ Context Augmentation*
- **Level 5 (13–15 คะแนน):** Dense RAG ทำงานครบถ้วนสมบูรณ์ตั้งแต่ `Embedding` $\rightarrow$ `Vector Retrieval` $\rightarrow$ `Context Selection` $\rightarrow$ `LLM` มีการปรับแต่ง Retrieval Hyperparameters เช่น Top-K, Similarity Threshold, Reranking Model หรือเทคนิคเฉพาะ พร้อมมีผลการทดลองเชิงประจักษ์ยืนยันคุณภาพ
- **Level 4 (10–12 คะแนน):** Dense RAG ทำงานได้ครบถ้วนและให้ผลลัพธ์ที่ถูกต้อง มีการกำหนด Retrieval Strategy และพารามิเตอร์อย่างชัดเจน
- **Level 3 (7–9 คะแนน):** Dense RAG ทำงานได้จริงตั้งแต่ Vector Search จนถึง LLM แต่ใช้ Configuration พื้นฐาน (Default parameters) และยังไม่มีการจูนปรับปรุงคุณภาพ
- **Level 2 (4–6 คะแนน):** สามารถทำ Vector Search ได้ แต่การส่งผ่าน Retrieval Context ไปให้ LLM ตอบคำถามยังไม่สมบูรณ์หรือไม่เสถียร
- **Level 1 (0–3 คะแนน):** มีเพียง Embedding หรือ Vector DB / Prototype แต่ไม่สามารถแสดงการทำงานของ Dense RAG ได้ครบกระบวนการ

---

### 3.3 Graph RAG (15 คะแนน)
*การออกแบบ Knowledge Graph, Entity/Relationship และ Graph Retrieval*
- **Level 5 (13–15 คะแนน):** มีการออกแบบ Knowledge Graph ที่ถูกต้องเหมาะสม มี Entities (Nodes) และ Relationships ที่มีความหมายเชื่อมโยงอย่างแท้จริง ใช้ Graph Retrieval ในการค้นหา Multi-hop Context เพื่อตอบคำถามจริง และสามารถอธิบาย/พิสูจน์ได้ว่า Graph ช่วยแก้ไขข้อจำกัดของ Dense Retrieval ได้อย่างไร
- **Level 4 (10–12 คะแนน):** Graph RAG ทำงานได้จริง มี Graph Query/Retrieval (เช่น Cypher หรือ Graph Traversal) และนำข้อมูลเข้าสู่ Context ของ LLM เพื่อสร้างคำตอบได้อย่างถูกต้อง
- **Level 3 (7–9 คะแนน):** มี Graph Database และสามารถดึงข้อมูลผ่าน Graph Retrieval มาร่วมกับ LLM ได้ แต่ Schema ของ Graph หรือการใช้ประโยชน์จาก Relationship ยังเป็นระดับพื้นฐาน
- **Level 2 (4–6 คะแนน):** สามารถสร้าง Node และ Relationship ใน Graph ได้ แต่การดึงข้อมูลมาใช้ในการ Retrieval หรือการสร้างคำตอบยังจำกัด
- **Level 1 (0–3 คะแนน):** มีเพียง Graph Database เปล่าหรือมี Node/Relationship ตัวอย่างเพียงไม่กี่จุด และยังไม่สามารถ Query ข้อมูลมาทำงานร่วมกับ RAG ได้จริง

---

### 3.4 Hybrid RAG (20 คะแนน) — ⭐ หัวใจสำคัญของโครงงาน
*การผสานรวม Dense Retrieval และ Graph Retrieval เข้าด้วยกันอย่างมีกลยุทธ์*
- **Level 5 (17–20 คะแนน):** สามารถบูรณาการ Dense Retrieval และ Graph Retrieval ได้อย่างเป็นระบบ ออกแบบกลยุทธ์ Hybrid ได้อย่างมีประสิทธิภาพ เช่น Reciprocal Rank Fusion (RRF), Dynamic Routing, Adaptive Re-ranking หรือ Context Aggregation ที่เหมาะสม พร้อมมีผลการทดลองยืนยันชัดเจนว่า Hybrid RAG เหนือกว่า Dense RAG เดี่ยวๆ หรือ Graph RAG เดี่ยวๆ อย่างไร
- **Level 4 (13–16 คะแนน):** สามารถใช้ Dense และ Graph Retrieval ร่วมกันได้จริง ออกแบบกระบวนการรวมผลลัพธ์ (Merging/Fusion) ชัดเจน และระบบทำงานได้อย่างมีเสถียรภาพ
- **Level 3 (9–12 คะแนน):** นำผลลัพธ์จากทั้ง Dense และ Graph มารวมกันในระบบเดียวกันได้ แต่การ Fusion หรือคัดเลือก Context ยังเป็นวิธีพื้นฐาน (เช่น นำมารวมกันตรงๆ แบบ Concatenate โดยไม่จัดลำดับความสำคัญ)
- **Level 2 (5–8 คะแนน):** มีทั้งโมดูล Dense และ Graph ในระบบ แต่ส่วนใหญ่แยกกันทำงาน หรือการเชื่อมโยงข้อมูลระหว่างสองระบบยังขาดความชัดเจน
- **Level 1 (0–4 คะแนน):** มีทั้งส่วน Dense และ Graph อยู่ในโค้ด แต่ไม่ได้ถูกนำมาประมวลผลร่วมกันเพื่อสร้างคำตอบสุดท้าย

---

### 3.5 Local LLM & API LLM (15 คะแนน)
*การเลือกใช้ การปรับแต่ง และการเปรียบเทียบระหว่างโมเดล Local และโมเดล Cloud API*
- **Level 5 (13–15 คะแนน):**
  - **Local LLM:** คัดเลือกโมเดลเหมาะสมกับสภาพ Hardware และประเภทงาน มีการปรับ Prompt, System Message, Context Window และมีการวัด Resource Usage (GPU/VRAM/RAM), Response Time อย่างเป็นระบบ
  - **API LLM:** นำโมเดลผ่าน Cloud API (เช่น OpenAI, Anthropic, Gemini) มาใช้งานจริง มีการจัดการ Prompt, Token Usage, Rate Limit, Error Handling และการวิเคราะห์ Cost/Latency เทียบกับ Local LLM อย่างละเอียด
- **Level 4 (10–12 คะแนน):** ทั้ง Local LLM และ API LLM เชื่อมต่อกับระบบ RAG ได้เป็นอย่างดี มีการเก็บข้อมูลวิเคราะห์การใช้ Resource และคุณภาพคำตอบ
- **Level 3 (7–9 คะแนน):** เชื่อมต่อ RAG ใช้งานได้ทั้ง Local LLM และ API LLM แต่ใช้ Configuration พื้นฐาน ยังไม่มีการวิเคราะห์เชิงลึกด้าน Token/Cost/Hardware
- **Level 2 (4–6 คะแนน):** เรียกใช้งาน Local LLM หรือ API LLM ได้ แต่การบูรณาการเข้ากับ Pipeline ของ RAG ยังมีข้อบกพร่องหรือไม่สมบูรณ์
- **Level 1 (0–3 คะแนน):** มีเพียงสคริปต์ทดสอบเรียกโมเดลเบื้องต้น แต่ไม่สามารถนำมาต่อเข้ากับระบบ RAG ในการประมวลผลจริงได้

---

### 3.6 System Integration (10 คะแนน)
*ความต่อเนื่องของ End-to-End Workflow, สถาปัตยกรรมระบบ และ Error Handling*
- **Level 5 (9–10 คะแนน):** ทุกองค์ประกอบเชื่อมต่อเป็น Pipeline เดียวกันอย่างสมบูรณ์แบบ: `User Query` $\rightarrow$ `Query Processing / Routing` $\rightarrow$ `Dense & Graph Retrieval` $\rightarrow$ `Hybrid Fusion` $\rightarrow$ `LLM Generation` $\rightarrow$ `Final Answer` พร้อมมี Error Handling, Fallback Mechanism และเอกสาร Architecture Diagram ที่ชัดเจน
- **Level 4 (7–8 คะแนน):** องค์ประกอบหลักทำงานร่วมกันได้ครบถ้วน Workflow ชัดเจน และระบบทำงานได้ราบรื่น
- **Level 3 (5–6 คะแนน):** ระบบทำงานได้ครบตาม Pipeline แต่ Architecture ยังเรียบง่าย ขาดการจัดการ Edge Case หรือ Exception Handling
- **Level 2 (3–4 คะแนน):** แต่ละโมดูลทำงานได้เดี่ยวๆ แต่การส่งผ่าน Input/Output ระหว่างส่วนต่างๆ ยังขัดข้องหรือเกิด Error บ่อยครั้ง
- **Level 1 (0–2 คะแนน):** ระบบแยกเป็น Prototype ย่อยๆ ที่ยังไม่เชื่อมต่อกันเป็น End-to-End Service

---

### 3.7 Evaluation & Experimental Analysis (10 คะแนน)
*การออกแบบการทดลอง ตัวชี้วัดเชิงปริมาณ (Metrics) และการวิเคราะห์สาเหตุของผลลัพธ์*
- **Level 5 (9–10 คะแนน):** ออกแบบการทดลองอย่างเป็นระบบ มี Test Benchmark/Dataset ที่ได้มาตรฐาน เปรียบเทียบผลลัพธ์ระหว่าง:
  - Dense RAG vs Graph RAG vs Hybrid RAG
  - Local LLM vs API LLM
  - มี Metrics ที่เหมาะสม (เช่น Retrieval Metrics: Hit Rate, MRR, NDCG และ Generation Metrics: Faithfulness, Answer Relevance, Semantic Similarity) พร้อมการวิเคราะห์เชิงลึกว่าทำไมวิธีหนึ่งถึงชนะอีกวิธีในแต่ละรูปแบบคำถาม
- **Level 4 (7–8 คะแนน):** มีการทดลองเปรียบเทียบหลาย Configuration พร้อมบันทึกตาราง Metrics และสรุปผลการวิเคราะห์
- **Level 3 (5–6 คะแนน):** มี Test Dataset และผลการรันวัดค่าเบื้องต้น แต่ยังขาดการวิเคราะห์เชิงลึกว่าผลลัพธ์เกิดจากสาเหตุใด
- **Level 2 (3–4 คะแนน):** มีการทดสอบระบบ แต่ไม่มีการบันทึกตัวชี้วัดหรือตารางเปรียบเทียบที่ชัดเจน
- **Level 1 (0–2 คะแนน):** แสดงเพียงตัวอย่างการตอบคำถามแบบ Demo ไม่กี่ข้อความ โดยไม่มีการประเมินผลเชิงวิทยาศาสตร์

---

### 3.8 Documentation & Presentation (5 คะแนน)
*ความสมบูรณ์ของเอกสาร โครงสร้างโค้ด และการนำเสนอ*
- **Level 5 (5 คะแนน):** เอกสารประกอบครบถ้วน (README, Architecture Diagram, การติดตั้ง, คู่มือทดสอบ), Code มีระเบียบและคอมเมนต์อธิบาย Flow การทำงานชัดเจน นำเสนอให้เห็นจุดเด่น ปัญหา และผลการทดลองได้อย่างยอดเยี่ยม
- **Level 4 (4 คะแนน):** เอกสารครบถ้วน โค้ดสะอาด รันตามขั้นตอนได้จริง
- **Level 3 (3 คะแนน):** เอกสารมีตามข้อกำหนดพื้นฐาน แต่ขาดรายละเอียดบางจุด
- **Level 2 (2 คะแนน):** เอกสารไม่ครบถ้วน โค้ดอ่านยากหรือติดตั้งตามได้ยาก
- **Level 1 (0–1 คะแนน):** ขาดเอกสารและคู่มือการรัน

---

## 4. ตัวอย่างการจำแนกระดับของ Project (Archetypes)

| ระดับโปรเจกต์ | ลักษณะของระบบและข้อจำกัดที่พบ |
| :---| :---|
| **Project A (Level 1)** | มี Vector Database, Neo4j, และ Ollama ติดตั้งอยู่ในเครื่อง แต่แต่ละส่วนแยกกันทำงาน ไม่ได้รวมเป็น Hybrid RAG และไม่มีการทดลองวัดผล |
| **Project B (Level 2)** | Dense RAG และ Graph RAG แยกกันทำงานเดี่ยวๆ ได้ แต่ยังไม่นำมาประกอบร่างเข้าด้วยกัน และไม่มีการทดสอบเปรียบเทียบผลลัพธ์อย่างเป็นระบบ |
| **Project C (Level 3)** | เชื่อมต่อครบทุกส่วน (Dense + Graph + Hybrid + Local LLM + API LLM) แต่วิธีการ Fusion Context เป็นแบบพื้นฐานมากๆ (เช่น นำข้อความมาต่อกันดื้อๆ) และมีผลทดสอบเพียงเบื้องต้น |
| **Project D (Level 4)** | องค์ประกอบครบและทำงานร่วมกันได้จริง มีการจูน Retrieval Strategy มีกลไก Fusion ชัดเจน และมีตารางทดลองเปรียบเทียบผลระหว่าง Dense, Graph และ Hybrid |
| **Project E (Level 5)** | สถาปัตยกรรมยอดเยี่ยม Hybrid RAG ได้รับการออกแบบอย่างเป็นวิทยาศาสตร์ (เช่น RRF / Dynamic Routing), มี Benchmark Test ครบวงจร, วิเคราะห์ลึกถึง Root Cause ว่าโจทย์แบบไหนเหมาะกับ Graph, แบบไหนเหมาะกับ Dense พร้อมเปรียบเทียบ Latency/Cost/Quality ของ Local LLM กับ API LLM ครบถ้วน |
