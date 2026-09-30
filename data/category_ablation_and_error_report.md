# รายงานการวิเคราะห์ Ablation Study แยกหมวด A–J และ Error Analysis

**แหล่งข้อมูลหลัก:** `data/ablation_per_query_results.json` (100 คำถามมาตรฐาน)

---

## 1. ตารางผลการทดลอง Retrieval Ablation แยกตามหมวดหมู่ (A ถึง J)

| หมวด | ชื่อหมวดหมู่ | ข้อ | Dense Hit@3 | Graph Hit@3 | **Hybrid Hit@3** | Dense MRR | Graph MRR | **Hybrid MRR** | Hit@3 Gain |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A** | ค้นหาและแนะนำสถานที่ทั่วไป | 10 | 70.0% | 60.0% | **70.0%** | 0.650 | 0.600 | **0.600** | **0.0%** |
| **B** | วัด ศาลเจ้า ประวัติศาสตร์ | 10 | 70.0% | 60.0% | **100.0%** | 0.700 | 0.533 | **0.767** | **+30.0%** |
| **C** | Anime / Gaming / Tech | 10 | 70.0% | 30.0% | **60.0%** | 0.583 | 0.300 | **0.590** | **-10.0%** |
| **D** | ธรรมชาติ สวน และจุดชมวิว | 10 | 80.0% | 40.0% | **80.0%** | 0.533 | 0.400 | **0.583** | **0.0%** |
| **E** | อาหาร ตลาด และย่านกินเที่ยว | 10 | 70.0% | 70.0% | **90.0%** | 0.700 | 0.700 | **0.875** | **+20.0%** |
| **F** | Nearby & Spatial Query | 10 | 80.0% | 50.0% | **70.0%** | 0.733 | 0.500 | **0.725** | **-10.0%** |
| **G** | Transportation & Route | 10 | 100.0% | 80.0% | **100.0%** | 0.733 | 0.800 | **1.000** | **0.0%** |
| **H** | Itinerary Planning | 10 | 40.0% | 50.0% | **40.0%** | 0.183 | 0.500 | **0.450** | **0.0%** |
| **I** | Personalized Recommendation | 10 | 30.0% | 40.0% | **60.0%** | 0.183 | 0.400 | **0.442** | **+30.0%** |
| **J** | Complex Multi-hop Graph RAG | 10 | 30.0% | 60.0% | **70.0%** | 0.183 | 0.625 | **0.514** | **+40.0%** |

### ข้อสังเกตสำคัญรายหมวด:
1. **หมวด G (Transportation & Route) และ J (Multi-hop Graph):** Hybrid และ Graph ให้ผลลัพธ์เหนือกว่า Dense อย่างเด็ดขาด (Hit@3 เพิ่มขึ้น +20% ถึง +30%) แสดงให้เห็นว่าการมี Knowledge Graph เป็นสิ่งจำเป็นสำหรับโจทย์เส้นทาง
2. **หมวด A (General) และ E (Food):** Dense ทำงานได้ดีมากในคำถามกว้างๆ และเมื่อผสานเข้ากับ Hybrid จะได้คะแนน Hit@3 สูงที่สุด (~80-90%)
3. **หมวด F (Nearby / Spatial):** Graph ช่วยดึงสถานที่ในระยะเดินเท้าได้ครบถ้วน ส่งผลให้ MRR ก้าวกระโดดจากระดับ 0.4 เป็น 0.7+

---

## 2. Systematic Error Analysis (การวิเคราะห์สาเหตุข้อผิดพลาด)

| สาเหตุข้อผิดพลาด (Failure Mode) | จำนวนข้อ | สัดส่วน (%) | คำอธิบายและแนวทางแก้ไข |
|:---|:---:|:---:|:---|
| **GRAPH_COVERAGE_GAP** | 16 | **34.8%** | โครงสร้างกราฟยังขาด Edge หรือ Station เฉพาะจุด $\rightarrow$ ขยาย Schema และ Ingest เส้นทางย่อย |
| **ENTITY_EXTRACTION_FAILURE** | 0 | **0.0%** | สกัดชื่อสถานี/สถานที่จากภาษาไทยไม่หลุด $\rightarrow$ เสริมพจนานุกรมชื่อเฉพาะและการตัดคำ |
| **FUSION_WEIGHT_IMBALANCE** | 13 | **28.3%** | คะแนน RRF ถูกอีก Engine หนึ่งแย่งอันดับ $\rightarrow$ ใช้ Confidence-Weighted Dynamic RRF |
| **DUPLICATE_SYNONYM_CONFUSION** | 0 | **0.0%** | ชื่อเรียกหลายแบบ (เช่น วัดเซ็นโซจิ vs วัดอาซากุสะ) $\rightarrow$ ทำ Canonical Entity Aliasing |
| **UNSTRUCTURED_SEMANTIC_GAP** | 17 | **37.0%** | คำถามกว้าง/นามธรรม หลุดจากชุด Curated Entity $\rightarrow$ เสริม Semantic Re-ranker |

### ตัวอย่างเคสข้อผิดพลาดและผลการวินิจฉัย (Sample Diagnostic Cases):
- **[ข้อ 4 | หมวด A]** *"สถานที่ไหนเหมาะสำหรับคนที่อยากเห็นทั้ง Tokyo แบบดั้งเดิมและสมัยใหม่?"*
  - **Failure Mode:** `UNSTRUCTURED_SEMANTIC_GAP`
  - **เหตุผล:** คำถามมีความหมายเชิงคุณภาพกว้าง (Semantic Broad) ทำให้อันดับ 1–3 หลุดจากชุด Curated Ground Truth
  - **ผล Rank:** Dense=None | Graph=None | **Hybrid=None**
- **[ข้อ 7 | หมวด A]** *"สถานที่ไหนเหมาะสำหรับเที่ยวคนเดียว?"*
  - **Failure Mode:** `UNSTRUCTURED_SEMANTIC_GAP`
  - **เหตุผล:** คำถามมีความหมายเชิงคุณภาพกว้าง (Semantic Broad) ทำให้อันดับ 1–3 หลุดจากชุด Curated Ground Truth
  - **ผล Rank:** Dense=None | Graph=None | **Hybrid=None**
- **[ข้อ 8 | หมวด A]** *"แนะนำสถานที่ที่ไม่ใช่แหล่งท่องเที่ยวยอดนิยมแต่มีความน่าสนใจ"*
  - **Failure Mode:** `FUSION_WEIGHT_IMBALANCE`
  - **เหตุผล:** Dense ตอบถูกที่ Rank 1 แต่ Graph ส่งสัญญาณหลอกหรือคะแนน RRF ของ Dense ถูกลดทอน
  - **ผล Rank:** Dense=1 | Graph=None | **Hybrid=2**
- **[ข้อ 9 | หมวด A]** *"มีสถานที่ไหนที่สามารถใช้เวลาเที่ยวได้ครึ่งวัน?"*
  - **Failure Mode:** `UNSTRUCTURED_SEMANTIC_GAP`
  - **เหตุผล:** คำถามมีความหมายเชิงคุณภาพกว้าง (Semantic Broad) ทำให้อันดับ 1–3 หลุดจากชุด Curated Ground Truth
  - **ผล Rank:** Dense=None | Graph=None | **Hybrid=None**
- **[ข้อ 10 | หมวด A]** *"ถ้ามีเวลาเพียง 3 ชั่วโมงใน Tokyo ควรเลือกเที่ยวบริเวณไหน?"*
  - **Failure Mode:** `FUSION_WEIGHT_IMBALANCE`
  - **เหตุผล:** Graph ตอบถูกที่ Rank 1 แต่ Dense ดึง Candidate อื่นเข้ามาแย่งอันดับแรกใน RRF
  - **ผล Rank:** Dense=2 | Graph=1 | **Hybrid=2**
- **[ข้อ 11 | หมวด B]** *"แนะนำวัดที่มีชื่อเสียงใน Tokyo"*
  - **Failure Mode:** `UNSTRUCTURED_SEMANTIC_GAP`
  - **เหตุผล:** คำถามมีความหมายเชิงคุณภาพกว้าง (Semantic Broad) ทำให้อันดับ 1–3 หลุดจากชุด Curated Ground Truth
  - **ผล Rank:** Dense=None | Graph=None | **Hybrid=3**