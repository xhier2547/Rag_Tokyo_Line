# รายงานการวิเคราะห์ Ablation Study แยกหมวด A–J และ Error Analysis

**แหล่งข้อมูลหลัก:** `data/ablation_per_query_results.json` (100 คำถามมาตรฐาน)

---

## 1. ตารางผลการทดลอง Retrieval Ablation แยกตามหมวดหมู่ (A ถึง J)

| หมวด | ชื่อหมวดหมู่ | ข้อ | Dense Hit@3 | Graph Hit@3 | **Hybrid Hit@3** | Dense MRR | Graph MRR | **Hybrid MRR** | Hit@3 Gain |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **A** | ค้นหาและแนะนำสถานที่ทั่วไป | 10 | 70.0% | 60.0% | **70.0%** | 0.650 | 0.600 | **0.650** | **0.0%** |
| **B** | วัด ศาลเจ้า ประวัติศาสตร์ | 10 | 70.0% | 60.0% | **100.0%** | 0.700 | 0.533 | **0.850** | **+30.0%** |
| **C** | Anime / Gaming / Tech | 10 | 70.0% | 30.0% | **80.0%** | 0.583 | 0.300 | **0.675** | **+10.0%** |
| **D** | ธรรมชาติ สวน และจุดชมวิว | 10 | 80.0% | 40.0% | **80.0%** | 0.533 | 0.400 | **0.625** | **0.0%** |
| **E** | อาหาร ตลาด และย่านกินเที่ยว | 10 | 70.0% | 70.0% | **90.0%** | 0.700 | 0.700 | **0.833** | **+20.0%** |
| **F** | Nearby & Spatial Query | 10 | 80.0% | 50.0% | **70.0%** | 0.733 | 0.500 | **0.678** | **-10.0%** |
| **G** | Transportation & Route | 10 | 100.0% | 80.0% | **100.0%** | 0.733 | 0.800 | **1.000** | **0.0%** |
| **H** | Itinerary Planning | 10 | 40.0% | 50.0% | **50.0%** | 0.183 | 0.500 | **0.463** | **+10.0%** |
| **I** | Personalized Recommendation | 10 | 30.0% | 40.0% | **70.0%** | 0.183 | 0.400 | **0.467** | **+40.0%** |
| **J** | Complex Multi-hop Graph RAG | 10 | 30.0% | 60.0% | **70.0%** | 0.183 | 0.625 | **0.692** | **+40.0%** |

### ข้อสังเกตสำคัญรายหมวด:
1. หมวดที่ Hybrid เพิ่ม Hit@3 จาก Dense มากที่สุดคือ **I (+40 จุด), J (+40 จุด), B (+30 จุด)** แสดงประโยชน์ของ Graph และ fusion ในคำถามที่มีโครงสร้างหรือเงื่อนไขหลายส่วน
2. Hybrid ยังถดถอยจาก Dense ในหมวด **F (-10 จุด)** จึงไม่ควรสรุปว่า Hybrid ชนะทุกประเภทคำถาม
3. หมวดที่ทำได้ดีที่สุดคือ **B** โดย Hybrid Hit@3 = 100% และ MRR = 0.850

---

## 2. Systematic Error Analysis (การวิเคราะห์สาเหตุข้อผิดพลาด)

| สาเหตุข้อผิดพลาด (Failure Mode) | จำนวนข้อ | สัดส่วน (%) | คำอธิบายและแนวทางแก้ไข |
|:---|:---:|:---:|:---|
| **GRAPH_COVERAGE_GAP** | 18 | **43.9%** | โครงสร้างกราฟยังขาด Edge หรือ Station เฉพาะจุด $\rightarrow$ ขยาย Schema และ Ingest เส้นทางย่อย |
| **ENTITY_EXTRACTION_FAILURE** | 0 | **0.0%** | สกัดชื่อสถานี/สถานที่จากภาษาไทยไม่หลุด $\rightarrow$ เสริมพจนานุกรมชื่อเฉพาะและการตัดคำ |
| **FUSION_WEIGHT_IMBALANCE** | 6 | **14.6%** | คะแนนจากบาง Engine ยังแย่งอันดับกัน $\rightarrow$ ปรับ intent-aware weights จาก validation set |
| **DUPLICATE_SYNONYM_CONFUSION** | 0 | **0.0%** | ชื่อเรียกหลายแบบ (เช่น วัดเซ็นโซจิ vs วัดอาซากุสะ) $\rightarrow$ ทำ Canonical Entity Aliasing |
| **UNSTRUCTURED_SEMANTIC_GAP** | 17 | **41.5%** | คำถามกว้าง/นามธรรมยังหลุดจากชุด Curated Entity $\rightarrow$ ขยายคำพ้องและ fine-tune Semantic Re-ranker |

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
- **[ข้อ 11 | หมวด B]** *"แนะนำวัดที่มีชื่อเสียงใน Tokyo"*
  - **Failure Mode:** `UNSTRUCTURED_SEMANTIC_GAP`
  - **เหตุผล:** คำถามมีความหมายเชิงคุณภาพกว้าง (Semantic Broad) ทำให้อันดับ 1–3 หลุดจากชุด Curated Ground Truth
  - **ผล Rank:** Dense=None | Graph=None | **Hybrid=2**
- **[ข้อ 13 | หมวด B]** *"มีศาลเจ้าที่น่าสนใจใกล้ Shibuya หรือ Harajuku หรือไม่?"*
  - **Failure Mode:** `FUSION_WEIGHT_IMBALANCE`
  - **เหตุผล:** Dense ตอบถูกที่ Rank 1 แต่ Graph ส่งสัญญาณหลอกหรือคะแนน RRF ของ Dense ถูกลดทอน
  - **ผล Rank:** Dense=1 | Graph=3 | **Hybrid=2**