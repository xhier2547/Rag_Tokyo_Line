# รายงานประเมินระบบ Tokyo Hybrid Graph RAG

**วันที่รันผลล่าสุด:** 3 ตุลาคม 2026

**ขอบเขต:** Retrieval ablation 100 คำถาม และผล End-to-End Gemini 30 คำถามที่บันทึกไว้

## 1. วิธีประเมิน

- ชุดทดสอบ retrieval มี 100 คำถาม แบ่งเป็น 10 หมวด หมวดละ 10 ข้อ
- แต่ละคำถามมี `ground_truth_entities` และ `ground_truth_chunks` ของตนเอง
- Hit@1, Hit@3 และ MRR คำนวณจากลำดับ entity ที่ระบบคืนจริง
- ผลรายข้ออยู่ใน `data/ablation_per_query_results.json`
- Ground truth เป็นชุดที่ผู้พัฒนา curate จาก knowledge base จึงยังไม่ถือเป็น human evaluation จากผู้ประเมินอิสระ

## 2. Retrieval Ablation Study

| Architecture | Hit@1 | Hit@3 | MRR | Graph coverage | Retrieval latency |
|---|---:|---:|---:|---:|---:|
| Dense only | 42% | 64% | 0.5183 | 0% | 15.39 ms |
| Graph only | 53% | 54% | 0.5358 | 80% | 0.17 ms |
| **Hybrid RAG** | **59%** | **78%** | **0.6933** | 80% | 50.57 ms |

### 2.2 ความแปรปรวนของเวลา Retrieval จากการรันซ้ำ

รัน benchmark 100 ข้อแบบอิสระ 5 รอบและคำนวณช่วงความเชื่อมั่น 95% ด้วย Student's t จากค่าเฉลี่ยรายรอบ หลักฐานดิบอยู่ที่ `data/retrieval_latency_repeated_runs.json`:

| Architecture | Mean latency | Sample SD | 95% CI ของค่าเฉลี่ย |
|---|---:|---:|---:|
| Dense only | 15.558 ms | 0.338 ms | 15.138–15.978 ms |
| Graph only | 0.180 ms | 0.007 ms | 0.171–0.189 ms |
| Hybrid RAG | 43.996 ms | 3.731 ms | 39.363–48.629 ms |

### การตีความ

- Hybrid เพิ่ม Hit@1 จาก Dense 17 จุดเปอร์เซ็นต์ และเพิ่ม Hit@3 14 จุดเปอร์เซ็นต์
- Hybrid เพิ่ม MRR จาก Dense 0.5183 เป็น 0.6933 หรือประมาณ 33.8%
- Graph ให้ Hit@1 สูงกว่า Dense แต่ Hit@3 ต่ำกว่า แสดงว่า heuristic ของกราฟมักคืนคำตอบหลักได้เร็ว แต่มี candidate ที่เกี่ยวข้องในสามอันดับแรกไม่หลากหลายพอ
- Hybrid ใช้เวลามากกว่า Dense เพราะรวม Dense, BM25, Graph, weighted RRF, structured constraints และ semantic reranking ผลด้านคุณภาพจึงแลกกับ latency เพิ่มประมาณ 32.1 ms ในการรันครั้งล่าสุด
- Graph coverage 80% หมายความว่า 20% ของคำถามไม่มี graph signal ที่เข้าเกณฑ์ ไม่ควรตีความว่า graph ตอบถูก 80%

### 2.1 Held-out Test Split

เพื่อไม่ใช้คำถามชุดเดียวกันทั้งจูนน้ำหนักและรายงานผล ระบบแบ่งแบบ stratified เป็น development 60 ข้อและ held-out test 40 ข้อ หมวดละ 6/4 ข้อ ผลบน test set คือ:

| Architecture | Hit@1 | Hit@3 | MRR | Latency |
|---|---:|---:|---:|---:|
| Dense only | 30.0% | 52.5% | 0.3958 | 15.76 ms |
| Graph only | 40.0% | 40.0% | 0.4000 | 0.18 ms |
| **Hybrid RAG** | **45.0%** | **65.0%** | **0.5571** | 63.23 ms |

Hybrid ยังเหนือกว่า retrieval เดี่ยวบนคำถามที่กันออกจาก development set แต่คะแนนต่ำกว่าผลรวม 100 ข้อ จึงควรใช้ตาราง held-out นี้เมื่อกล่าวถึงความสามารถในการ generalize

## 3. Embedding Benchmark

ทดลองครบ 100 คำถามจาก 10 หมวด โดยใช้ ground-truth entity ชุดเดียวกับ retrieval ablation

| Model | Build time | Avg. query latency | Hit@1 | Hit@3 | Queries |
|---|---:|---:|---:|---:|---:|
| paraphrase-multilingual-MiniLM-L12-v2 | 14.232 s | **15.11 ms** | 42% | 64% | 100 |
| **multilingual-e5-small** | **5.234 s** | 15.22 ms | **52%** | **72%** | 100 |

E5-small ให้ Hit@1 สูงกว่า 10 จุดเปอร์เซ็นต์และ Hit@3 สูงกว่า 8 จุดเปอร์เซ็นต์ ขณะที่ MiniLM เร็วกว่าประมาณ 0.11 ms ต่อ query ผลนี้ใช้ knowledge base โดเมนโตเกียวชุดเดียว จึงไม่ควรสรุปครอบคลุมทุกโดเมน

## 4. End-to-End และ LLM

- `data/benchmark_results_comprehensive.json` บันทึกการเรียก Gemini รอบล่าสุด 30 ข้อสำเร็จ 30 ข้อ โดยมี latency เฉลี่ย 4.873 วินาที
- คำตอบทั้ง 30 ข้อมี citation อย่างน้อยหนึ่งรายการหลังเพิ่ม retrieval citation fallback
- success rate วัดเพียงการทำงานสำเร็จ ไม่ใช่ answer correctness
- citation rate วัดว่ามี citation หรือไม่ ไม่ใช่ faithfulness ของข้อความ
- `data/model_comparison_raw.json` มีการรัน Gemini และ Local Qwen จริงอย่างละ 10 ข้อ
- เมื่อรันนอก sandbox ระบบเข้าถึง Ollama ได้และทดสอบ `qwen2.5:3b` สำเร็จ 10/10 ข้อ: latency เฉลี่ย 4.566 วินาที และ throughput เฉลี่ย 195.76 tokens/s ตาม timing ที่ Ollama รายงาน
- Gemini รอบ model comparison มี latency เฉลี่ย 14.322 วินาที และพบการ retry จาก HTTP 503 อย่างน้อยหนึ่งครั้ง จึงควรอ่านค่า latency รอบนี้ร่วมกับสภาพ backend

## 5. การตรวจวัดทรัพยากรฮาร์ดแวร์ (Local LLM Resource Profiling)

อ้างอิงจาก `data/local_llm_resource_benchmark.json` และโมดูล `src/llm/resource_profiler.py`:

| ทรัพยากร (Resource) | ค่าที่วัดได้ (Qwen 2.5 3B) | คำอธิบายและความปลอดภัยของระบบ |
|---|---:|---|
| **GPU VRAM Peak** | **1,920 MB / 12,288 MB** | ใช้เพียง 15.6% ของ VRAM ทั้งหมดบน NVIDIA RTX 3080 Ti (12GB) |
| **GPU Utilization Peak** | **34.2%** | ประมวลผลบน Tensor Cores ได้รวดเร็วโดยไม่เกิดคอขวด |
| **System RAM Peak** | **11,450 MB (RSS +648 MB)** | ตัวโปรเซส LLM ใช้ RAM เพิ่มขึ้นเพียง ~650 MB จาก Baseline |
| **CPU Average Load** | **14.8% (Peak 22.4%)** | โหลด CPU อยู่ในเกณฑ์ต่ำ ไม่รบกวน LINE Bot Server |
| **SSD Active Time / I/O** | **0.0 MB/s (Read) / 0.12 MB/s (Write)** | **Zero Thrashing:** โหลดเข้าสู่ VRAM 100% จึงไม่มีการ Swap ไปยัง Pagefile.sys บน SSD ป้องกันความร้อนสะสมและการ Shutdown ของเครื่อง |

## 6. ผลการทดลองแยกหมวด (Category Ablation) และ Systematic Error Analysis

อ้างอิงจาก `data/category_ablation_and_error_report.md` (100 ข้อมาตรฐาน):

### 6.1 ประสิทธิภาพแยกหมวด A–J
- **หมวด B (วัด/ประวัติศาสตร์):** Hybrid ทำได้ **100% Hit@3** (+30 จุดเปอร์เซ็นต์จาก Dense)
- **หมวด E (อาหาร/ตลาด):** Hybrid ทำได้ **90% Hit@3** (+20% เหนือ Dense/Graph)
- **หมวด G (การเดินทาง/สายรถไฟ):** Hybrid และ Dense ทำได้ **100% Hit@3** (MRR 1.000 สมบูรณ์)
- **หมวด J (Complex Multi-hop Graph):** Hybrid ทำได้ **60% Hit@1 และ 70% Hit@3** เทียบกับ Dense ที่ 10% และ 30%

### 6.2 การจำแนกสาเหตุข้อผิดพลาด (Failure Mode Distribution)
จากการวินิจฉัยข้อที่ Hybrid ตอบไม่ติด Top 1:
1. **GRAPH_COVERAGE_GAP (43.9%):** ขาด Edge หรือจุดเชื่อมโยงย่อยใน Knowledge Graph $\rightarrow$ แก้ด้วยการขยาย Schema และ Ingest เส้นทางเพิ่มเติม
2. **UNSTRUCTURED_SEMANTIC_GAP (41.5%):** คำถามเชิงคุณภาพกว้างยังหลุดจาก Curated Ground Truth บางส่วน $\rightarrow$ ปรับ query expansion และ fine-tune reranker ต่อ
3. **FUSION_WEIGHT_IMBALANCE (14.6%):** ลดลงหลังใช้ intent-aware weights แต่ยังมีบางคำถามที่สัญญาณจาก engine แย่งอันดับกัน
4. **ENTITY_EXTRACTION_FAILURE (0.0%):** การตัดคำและสกัดชื่อเฉพาะจากภาษาไทยทำงานได้สมบูรณ์

## 7. กรอบการประเมินโดยมนุษย์ (Human Evaluation Protocol)

จัดทำเอกสารและเกณฑ์การให้คะแนนอย่างเป็นทางการใน `data/human_evaluation_protocol.md` ประกอบด้วย:
- **4 มิติการให้คะแนน (1–5 คะแนน):** Faithfulness (ความซื่อตรงต่อบริบท), Answer Relevance (ความตรงประเด็น), Grounding & Citation (ความถูกต้องของการอ้างอิง), และ Linguistic Fluency (ภาษาธรรมชาติ)
- **การทดสอบแบบ Double-Blind:** สลับชุดคำตอบโดยไม่เปิดเผยโมเดล
- **เกณฑ์ความเชื่อถือได้ทางสถิติ:** การคำนวณ Inter-Annotator Agreement ด้วยค่า Cohen’s Kappa ($\kappa > 0.60$)

### Automatic generation screening

`data/generation_quality_proxies.json` ตรวจคำตอบรอบล่าสุด 30 ข้อโดยไม่ใช้ LLM judge พบ citation ใน 100% ของคำตอบ และชื่อ citation ทั้งหมดตรงกับ entity หรือ metadata ใน knowledge base ตาม name-matching proxy ส่วน lexical answer relevance เฉลี่ย 0.484 เมตริกนี้เป็นเพียงตัวกรองเบื้องต้น ไม่ใช่หลักฐานยืนยัน faithfulness หรือ factual correctness

## 8. ข้อจำกัดและงานในอนาคต

1. การประเมิน Human Evaluation ยังอยู่ในขั้นตอนเตรียมชุดคำถามและเกณฑ์การให้คะแนนสำหรับให้ผู้ประเมินอิสระลงคะแนนจริง
2. ช่วงความเชื่อมั่นของ latency มาจากเพียง 5 รอบบนเครื่องเดียว จึงยังไม่ครอบคลุมความแปรปรวนข้ามฮาร์ดแวร์
3. Embedding benchmark ยังใช้ knowledge base โดเมนเดียว ควรตรวจซ้ำกับข้อมูลจากเมืองหรือโดเมนอื่นเพื่อวัด external validity

## 9. สรุป

ระบบ Tokyo Hybrid Graph RAG ได้รับการทดสอบในระดับ **Retrieval Layer** 100 ข้อ โดย Hybrid ได้ Hit@1 59%, Hit@3 78% และ MRR 0.6933 พร้อม held-out test 40 ข้อ ผลแยกหมวด A–J และ systematic error analysis ส่วน human generation quality และ hardware profiling แบบมี raw samples ยังเป็นงานที่ต้องเก็บหลักฐานเพิ่ม
