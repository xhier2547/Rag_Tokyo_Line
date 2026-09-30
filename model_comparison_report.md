# รายงานเปรียบเทียบ Embedding และ LLM

**วันที่รันผลล่าสุด:** 30 กันยายน 2026

**หลักฐานดิบ:** `data/processed/embedding_benchmark_results.json` และ `data/model_comparison_raw.json`

## 1. Embedding Models

การทดลองใช้ 30 คำถามจาก 10 หมวด หมวดละ 3 ข้อ และวัดการพบ ground-truth entity ในอันดับ 1 และ 3

![Embedding benchmark](reports/charts/chart_1_embedding_comparison.png)

| Model | Dimensions | Build time | Query latency | Hit@1 | Hit@3 |
|---|---:|---:|---:|---:|---:|
| paraphrase-multilingual-MiniLM-L12-v2 | 384 | 20.323 s | **16.45 ms** | 47% | 67% |
| **multilingual-e5-small** | 384 | **12.405 s** | 18.39 ms | **70%** | **80%** |

### ข้อสรุปจากผลที่วัดได้

- E5-small เหนือกว่า MiniLM 23 จุดเปอร์เซ็นต์ที่ Hit@1 และ 13 จุดเปอร์เซ็นต์ที่ Hit@3
- MiniLM มี query latency ต่ำกว่า 1.94 ms
- หากเน้น accuracy ผลรอบนี้สนับสนุน E5-small หากเน้น latency และ compatibility กับระบบเดิม MiniLM ยังใช้งานได้
- ไม่มีผล BGE-M3 ใน artifact ปัจจุบัน จึงไม่นำมาเปรียบเทียบ

## 2. LLM และ Fallback

สคริปต์ `src/evaluation/generate_model_comparison_raw.py` จะรายงานเฉพาะ backend ที่เรียกใช้งานจริง หาก Ollama ไม่พร้อมจะไม่สร้างตัวเลขจำลอง

| Backend | สถานะ | Queries | Avg. latency | หมายเหตุ |
|---|---|---:|---:|---|
| Gemini 3.1 Flash Lite | Measured live | 10 | 14.322 s | เรียก Cloud API จริง; รอบนี้มี retry จาก HTTP 503 |
| Local Ollama (`Qwen 2.5 3B`) | Measured live | 10 | **4.566 s** | สำเร็จ 10/10 ข้อ, throughput เฉลี่ย 195.76 tokens/s ตาม Ollama timing |
| Deterministic fallback | Measured locally | 10 | 0.0003 s | เป็น retrieval fallback ไม่ใช่ generative LLM |

Local Qwen เร็วกว่า Gemini ในรอบนี้ประมาณ 3.14 เท่า (4.566 เทียบกับ 14.322 วินาที) แต่ latency ของ Gemini รอบนี้ได้รับผลจากการ retry หลัง backend ตอบ 503 อย่างน้อยหนึ่งครั้ง จึงไม่ควรตีความว่าเป็นความเร็วปกติของ API ทุกครั้ง ค่าของ deterministic fallback ใช้เปรียบเทียบ latency กับ LLM โดยตรงไม่ได้ เพราะ fallback ไม่ได้สร้างภาษาด้วยโมเดล

### 2.1 Hardware Resource Measurement (Qwen 2.5 3B บน RTX 3080 Ti)

วัดผลผ่าน `src/llm/resource_profiler.py` บันทึกใน `data/local_llm_resource_benchmark.json`:

| Hardware Metric | ค่าที่วัดได้จริง | สถานะการทำงาน |
|---|---:|---|
| **GPU VRAM Peak** | **1,920 MB** (จาก 12,288 MB) | โหลดโมเดลเข้า VRAM 100% |
| **GPU Utilization Peak** | **34.2%** | ประมวลผลลื่นไหล |
| **System RAM Peak** | **11,450 MB** (+648.5 MB RSS) | กิน RAM เพิ่มเล็กน้อย |
| **CPU Average Load** | **14.8%** (Peak 22.4%) | ไม่เกิดคอขวด CPU |
| **SSD Active Time / Write** | **0.12 MB/s** | **Zero Thrashing:** ไม่แตะ Swap ป้องกันความร้อนสะสมและการ Shutdown ของเครื่อง |

## 3. สิ่งที่ยังสรุปไม่ได้และงานถัดไป

- การเปรียบเทียบคุณภาพภาษาเชิงลึก (Faithfulness, Fluency) อยู่ในขั้นตอนจัดทำร่วมกับ [Human Evaluation Protocol](file:///data/human_evaluation_protocol.md)
- ยังไม่มีผล semantic similarity เทียบกับคำตอบมนุษย์ (Ground Truth Reference)
- success และ citation presence ไม่เท่ากับความถูกต้องหรือ zero hallucination ทั้ง 100% โดยต้องตรวจสอบผ่าน Error Analysis ร่วมด้วย

## 4. วิธีทำซ้ำ

```powershell
python src/vector/benchmark_embeddings.py
python src/evaluation/generate_model_comparison_raw.py
python src/evaluation/run_comprehensive_eval.py --ablation-only
```

การรัน LLM comparison ต้องมี Gemini API key ส่วน Local LLM ต้องเปิด Ollama และมีโมเดลที่กำหนดไว้ใน configuration
