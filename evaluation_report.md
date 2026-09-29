# รายงานประเมินระบบ Tokyo Hybrid Graph RAG

**วันที่รันผลล่าสุด:** 30 กันยายน 2026

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
| Dense only | 42% | 64% | 0.5183 | 0% | 15.08 ms |
| Graph only | 53% | 54% | 0.5358 | 80% | 0.16 ms |
| **Hybrid RAG** | **54%** | **74%** | **0.6546** | 80% | 27.36 ms |

### การตีความ

- Hybrid เพิ่ม Hit@1 จาก Dense 12 จุดเปอร์เซ็นต์ และเพิ่ม Hit@3 10 จุดเปอร์เซ็นต์
- Hybrid เพิ่ม MRR จาก Dense 0.5183 เป็น 0.6546 หรือประมาณ 26.3%
- Graph ให้ Hit@1 สูงกว่า Dense แต่ Hit@3 ต่ำกว่า แสดงว่า heuristic ของกราฟมักคืนคำตอบหลักได้เร็ว แต่มี candidate ที่เกี่ยวข้องในสามอันดับแรกไม่หลากหลายพอ
- Hybrid ใช้เวลามากกว่า Dense เพราะรวม Dense, BM25, Graph และ RRF ผลด้านคุณภาพจึงแลกกับ latency เพิ่มประมาณ 12 ms ในการรันครั้งล่าสุด
- Graph coverage 80% หมายความว่า 20% ของคำถามไม่มี graph signal ที่เข้าเกณฑ์ ไม่ควรตีความว่า graph ตอบถูก 80%

## 3. Embedding Benchmark

ทดลอง 30 คำถาม โดยเลือก 3 ข้อต่อหมวดจาก benchmark เดียวกัน

| Model | Build time | Avg. query latency | Hit@1 | Hit@3 | Queries |
|---|---:|---:|---:|---:|---:|
| paraphrase-multilingual-MiniLM-L12-v2 | 20.323 s | **16.45 ms** | 47% | 67% | 30 |
| **multilingual-e5-small** | **12.405 s** | 18.39 ms | **70%** | **80%** | 30 |

E5-small ให้ retrieval accuracy สูงกว่าในการทดลองนี้ ส่วน MiniLM เร็วกว่าประมาณ 1.94 ms ต่อ query การทดลองยังมีขนาดเล็กและใช้ knowledge base ชุดเดียว จึงไม่ควรสรุปผลครอบคลุมทุกโดเมน

## 4. End-to-End และ LLM

- artifact เดิม `data/benchmark_results_comprehensive.json` บันทึกการเรียก Gemini 30 ข้อสำเร็จ 30 ข้อ
- success rate วัดเพียงการทำงานสำเร็จ ไม่ใช่ answer correctness
- citation rate วัดว่ามี citation หรือไม่ ไม่ใช่ faithfulness ของข้อความ
- `data/model_comparison_raw.json` มีการรัน Gemini และ Local Qwen จริงอย่างละ 10 ข้อ
- เมื่อรันนอก sandbox ระบบเข้าถึง Ollama ได้และทดสอบ `qwen2.5:3b` สำเร็จ 10/10 ข้อ: latency เฉลี่ย 4.566 วินาที และ throughput เฉลี่ย 195.76 tokens/s ตาม timing ที่ Ollama รายงาน
- Gemini รอบ model comparison มี latency เฉลี่ย 14.322 วินาที และพบการ retry จาก HTTP 503 อย่างน้อยหนึ่งครั้ง จึงควรอ่านค่า latency รอบนี้ร่วมกับสภาพ backend

## 5. ข้อจำกัด

1. ยังไม่มี human judge หรือผู้ประเมินอิสระตรวจความถูกต้องของ ground truth และคำตอบ
2. ยังไม่มี generation metrics เช่น faithfulness, answer relevance หรือ semantic similarity ที่ผ่าน evaluator แยกต่างหาก
3. ยังไม่มีการวัด RAM, VRAM และ CPU ของ Local LLM แม้มี latency และ throughput จริงแล้ว
4. ยังไม่มี repeated runs หรือ confidence interval สำหรับ latency และ retrieval metrics
5. ผล embedding 30 ข้อเหมาะสำหรับ model screening มากกว่าการสรุปเชิงสถิติขั้นสุดท้าย

## 6. สรุป

หลักฐานปัจจุบันสนับสนุนว่า RRF Hybrid ช่วยเพิ่ม Hit@3 และ MRR เมื่อเทียบกับ Dense และ Graph แบบเดี่ยวในชุดทดสอบ 100 ข้อ และยืนยันว่า Gemini กับ Qwen 2.5 3B เชื่อมต่อ pipeline ได้จริง ระบบยังขาด resource measurement และการประเมินคุณภาพ generation โดยผู้ประเมินอิสระ จึงยังไม่อ้างว่าองค์ประกอบทั้งหมดผ่าน Rubric Level 5
