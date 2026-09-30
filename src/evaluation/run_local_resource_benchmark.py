"""
src/evaluation/run_local_resource_benchmark.py
=============================================
รันวัดผลการใช้ทรัพยากรจริงของ Local LLM (qwen2.5:3b)
วัดแบบ Real-time ขนานไปกับการตอบคำถาม 10 ข้อ:
- RAM (System & Process RSS, Peak Memory)
- CPU Load (% เฉลี่ย และ Peak %)
- GPU VRAM (Used MB, Delta MB, Peak VRAM)
- GPU Utilization %
- Latency & Token Throughput (tokens/s)
บันทึกลง data/local_llm_resource_benchmark.json และอัปเดต data/model_comparison_raw.json
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from src.hybrid.engine import TokyoHybridRAGEngine
from src.llm.local_llm import LocalLLMClient
from src.evaluation.generate_model_comparison_raw import BENCHMARK_PROMPTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_benchmark() -> Dict[str, Any]:
    print("=" * 70)
    print("🔬 RUNNING LIVE HARDWARE PROFILING FOR LOCAL LLM (3B-4B)")
    print("=" * 70)

    client = LocalLLMClient(model_name="qwen2.5:3b")
    health = client.check_health()
    if health.get("status") != "online":
        print(f"❌ Ollama is offline: {health.get('error')}")
        return {}

    print(f"✅ Local LLM Online: {client.model_name} via {client.base_url}")
    print(f"⚡ Starting 10-query benchmark with continuous hardware profiling...\n")

    hybrid_engine = TokyoHybridRAGEngine()

    results = []
    latencies = []
    throughputs = []
    peak_rams = []
    peak_vrams = []
    avg_cpus = []
    peak_gpus = []

    for idx, item in enumerate(BENCHMARK_PROMPTS):
        q = item["query"]
        cat = item["category"]
        cat_name = item["category_name"]
        print(f"[{idx+1}/10] หมวด {cat} ({cat_name}): '{q[:35]}...'")

        # 1. Hybrid Context Retrieval
        t_ret_start = time.perf_counter()
        hyb_res = hybrid_engine.retrieve_hybrid_context(q)
        ret_latency = time.perf_counter() - t_ret_start

        # 2. Local LLM Generation with live hardware profiling
        resp = client.answer_rag_query(
            query=q,
            context=hyb_res.final_context,
            profile_hardware=True
        )

        hw = resp.hardware_profile or {}
        cpu_info = hw.get("cpu", {})
        ram_info = hw.get("ram", {})
        gpu_info = hw.get("gpu", {})

        print(f"   ⏱️ Latency: {resp.latency_sec:.2f}s | Speed: {resp.tokens_per_sec:.1f} tok/s | Tokens: {resp.completion_tokens}")
        print(f"   💻 CPU: {cpu_info.get('avg_cpu_percent', 0)}% (Peak: {cpu_info.get('peak_cpu_percent', 0)}%) | RAM Peak: {ram_info.get('peak_ram_mb', 0):.0f} MB")
        if gpu_info.get("available"):
            print(f"   🎮 VRAM: {gpu_info.get('peak_vram_mb', 0):.0f} MB / {gpu_info.get('total_vram_mb', 0):.0f} MB | GPU Util: {gpu_info.get('peak_gpu_util_percent', 0)}%")
        print()

        latencies.append(resp.latency_sec)
        throughputs.append(resp.tokens_per_sec)
        if ram_info.get("peak_ram_mb"):
            peak_rams.append(ram_info["peak_ram_mb"])
        if gpu_info.get("peak_vram_mb"):
            peak_vrams.append(gpu_info["peak_vram_mb"])
        if cpu_info.get("avg_cpu_percent"):
            avg_cpus.append(cpu_info["avg_cpu_percent"])
        if gpu_info.get("peak_gpu_util_percent"):
            peak_gpus.append(gpu_info["peak_gpu_util_percent"])

        record = {
            "test_id": idx + 1,
            "category": cat,
            "category_name": cat_name,
            "query": q,
            "retrieval_latency_ms": round(ret_latency * 1000, 2),
            "generation": {
                "model": resp.model,
                "latency_sec": resp.latency_sec,
                "prompt_tokens": resp.prompt_tokens,
                "completion_tokens": resp.completion_tokens,
                "total_tokens": resp.total_tokens,
                "tokens_per_sec": resp.tokens_per_sec,
                "citations_count": len(resp.citations),
                "citations": resp.citations,
                "sample_preview": resp.text[:200] + "..."
            },
            "hardware_profile": hw
        }
        results.append(record)
        time.sleep(0.3)

    summary = {
        "model": client.model_name,
        "queries_evaluated": len(results),
        "avg_latency_sec": round(sum(latencies) / len(latencies), 3),
        "avg_tokens_per_sec": round(sum(throughputs) / len(throughputs), 2),
        "resource_metrics": {
            "avg_cpu_load_pct": round(sum(avg_cpus) / len(avg_cpus), 1) if avg_cpus else 0.0,
            "avg_peak_system_ram_mb": round(sum(peak_rams) / len(peak_rams), 1) if peak_rams else 0.0,
            "avg_peak_vram_mb": round(sum(peak_vrams) / len(peak_vrams), 1) if peak_vrams else None,
            "avg_peak_gpu_util_pct": round(sum(peak_gpus) / len(peak_gpus), 1) if peak_gpus else None,
            "gpu_device": results[0]["hardware_profile"].get("gpu", {}).get("name") if results else None
        }
    }

    payload = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "device": "Local Host (Ollama Runtime)"
        },
        "summary": summary,
        "details": results
    }

    out_file = os.path.join(BASE_DIR, "data", "local_llm_resource_benchmark.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("=" * 70)
    print(f"📊 SUMMARY OF MEASURED LOCAL RESOURCE USAGE ({client.model_name}):")
    print(f"  • Avg Latency: {summary['avg_latency_sec']} s")
    print(f"  • Avg Throughput: {summary['avg_tokens_per_sec']} tokens/s")
    print(f"  • CPU Load: ~{summary['resource_metrics']['avg_cpu_load_pct']}%")
    print(f"  • Peak VRAM: ~{summary['resource_metrics']['avg_peak_vram_mb']} MB (GPU: {summary['resource_metrics']['gpu_device']})")
    print(f"✅ Saved to: {out_file}")
    print("=" * 70)

    # ปรับปรุง data/model_comparison_raw.json ด้วยตัวเลขจริง
    update_model_comparison_raw(payload)

    return payload


def update_model_comparison_raw(bench_data: Dict[str, Any]):
    raw_path = os.path.join(BASE_DIR, "data", "model_comparison_raw.json")
    if not os.path.exists(raw_path):
        return

    try:
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        details = bench_data.get("details", [])
        detail_map = {d["test_id"]: d for d in details}

        for item in raw_data.get("raw_results", []):
            tid = item.get("test_id")
            if tid in detail_map:
                bench_item = detail_map[tid]
                hw = bench_item.get("hardware_profile", {})
                gen = bench_item.get("generation", {})
                item["local_ollama_3b"] = {
                    "model": gen.get("model", "qwen2.5:3b"),
                    "latency_sec": gen.get("latency_sec"),
                    "prompt_tokens": gen.get("prompt_tokens"),
                    "completion_tokens": gen.get("completion_tokens"),
                    "tokens_per_sec": gen.get("tokens_per_sec"),
                    "citations_count": gen.get("citations_count"),
                    "citations": gen.get("citations"),
                    "success": True,
                    "sample_output_preview": gen.get("sample_preview"),
                    "status": "MEASURED_LIVE",
                    "resource_usage": {
                        "cpu_avg_pct": hw.get("cpu", {}).get("avg_cpu_percent"),
                        "cpu_peak_pct": hw.get("cpu", {}).get("peak_cpu_percent"),
                        "ram_peak_mb": hw.get("ram", {}).get("peak_ram_mb"),
                        "process_rss_peak_mb": hw.get("ram", {}).get("process_rss_peak_mb"),
                        "vram_peak_mb": hw.get("gpu", {}).get("peak_vram_mb"),
                        "gpu_util_peak_pct": hw.get("gpu", {}).get("peak_gpu_util_percent")
                    }
                }

        # อัปเดต summary
        raw_data["summary"]["local_ollama_resource_measured"] = True
        raw_data["summary"]["local_ollama_avg_peak_vram_mb"] = bench_data["summary"]["resource_metrics"]["avg_peak_vram_mb"]
        raw_data["summary"]["local_ollama_avg_cpu_pct"] = bench_data["summary"]["resource_metrics"]["avg_cpu_load_pct"]

        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Updated {raw_path} with verified live hardware metrics!")
    except Exception as e:
        logger.error(f"Failed to update model_comparison_raw.json: {e}")


if __name__ == "__main__":
    run_benchmark()
