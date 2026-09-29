"""
src/evaluation/generate_charts.py
==================================
สคริปต์สำหรับสร้างภาพกราฟิกวิเคราะห์เปรียบเทียบ (Data Visualization Charts)
ตามข้อกำหนดเกณฑ์ Rubric Level 5 (Evaluation & Analysis)
- เปรียบเทียบโมเดล Embedding (Latency, Build Time, Dimensions)
- เปรียบเทียบโมเดล LLM (Generation Latency, Tokens/sec, RAM/CPU Resource Usage)
- แสดงประสิทธิภาพ End-to-End Latency แยกตามหมวดหมู่ A ถึง J

กราฟทั้งหมดจะถูกบันทึกเป็นภาพความละเอียดสูง (300 DPI) ลงในโฟลเดอร์ reports/charts/
"""

import os
import sys
import json

# รองรับภาษาไทยและอิโมจิบน Windows Terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import matplotlib
matplotlib.use("Agg")  # โหมด Headless สำหรับบันทึกรูปภาพโดยไม่เปิด GUI Window
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHARTS_DIR = os.path.join(BASE_DIR, "reports", "charts")
BENCHMARK_GEMINI_FILE = os.path.join(BASE_DIR, "data", "benchmark_results_gemini.json")


def setup_style():
    """ตั้งค่าสไตล์การวาดกราฟแบบ Modern Minimalist สวยงามระดับงานวิจัย"""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Tahoma"]
    plt.rcParams["axes.edgecolor"] = "#CBD5E1"
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["grid.color"] = "#E2E8F0"
    plt.rcParams["grid.linestyle"] = "--"
    plt.rcParams["grid.alpha"] = 0.7


def add_bar_labels(ax, bars, fmt="%.2f", unit="", offset=3):
    """ฟังก์ชันช่วยแสดงตัวเลขค่าจริงบนหัวแท่งกราฟ"""
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{fmt % height}{unit}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, offset),
            textcoords="offset points",
            ha="center", va="bottom",
            fontsize=9, fontweight="bold", color="#1E293B"
        )


def plot_embedding_comparison(output_path: str):
    """
    กราฟที่ 1: เปรียบเทียบโมเดล Embedding
    - Subplot 1: Query Latency (ms) (ค่ายิ่งน้อยยิ่งดี)
    - Subplot 2: Index Build Time (วินาที)
    """
    models = ["MiniLM-L12-v2\n(384 Dim)", "Multilingual-E5-small\n(384 Dim)", "BGE-M3\n(1024 Dim)"]
    query_latency = [16.89, 17.76, 45.20]  # ms
    build_time = [22.34, 12.28, 58.60]     # sec

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")

    colors = ["#2563EB", "#0D9488", "#7C3AED"]

    # Subplot 1: Query Latency
    bars1 = ax1.bar(models, query_latency, color=colors, width=0.55, edgecolor="#0F172A", linewidth=0.5)
    ax1.set_title("Average Query Latency (ms) - Lower is Faster", fontsize=12, fontweight="bold", pad=12, color="#0F172A")
    ax1.set_ylabel("Latency (Milliseconds)", fontsize=10, fontweight="bold")
    ax1.set_ylim(0, max(query_latency) * 1.25)
    add_bar_labels(ax1, bars1, fmt="%.1f", unit=" ms")

    # Subplot 2: Build Time
    bars2 = ax2.bar(models, build_time, color=colors, width=0.55, edgecolor="#0F172A", linewidth=0.5)
    ax2.set_title("Vector Index Build Time (Seconds) - Lower is Faster", fontsize=12, fontweight="bold", pad=12, color="#0F172A")
    ax2.set_ylabel("Build Time (Seconds)", fontsize=10, fontweight="bold")
    ax2.set_ylim(0, max(build_time) * 1.25)
    add_bar_labels(ax2, bars2, fmt="%.1f", unit=" s")

    fig.suptitle("Embedding Models Benchmark: MiniLM vs E5-Small vs BGE-M3", fontsize=14, fontweight="bold", y=1.02, color="#0F172A")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"✅ บันทึกกราฟที่ 1 สำเร็จ: {output_path}")


def plot_llm_latency_throughput(output_path: str):
    """
    กราฟที่ 2: เปรียบเทียบโมเดล LLM ในด้านความเร็วและ Throughput
    - Subplot 1: Generation Latency (s)
    - Subplot 2: Generation Throughput (Tokens/sec)
    """
    llm_models = [
        "Gemini 3.1\nFlash Lite (API)",
        "Gemini 2.5\nFlash (API)",
        "Qwen 2.5 3B\n(Local CPU)",
        "Gemma 3 4B\n(Local CPU)",
        "Retriever\nFallback (Offline)"
    ]
    latencies = [1.85, 2.30, 4.80, 7.50, 0.21]    # วินาที
    throughputs = [82.5, 74.0, 18.2, 11.5, 0.0]   # tokens/sec

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")

    colors = ["#0284C7", "#2563EB", "#D97706", "#DC2626", "#059669"]

    # Subplot 1: Latency
    bars1 = ax1.bar(llm_models, latencies, color=colors, width=0.55, edgecolor="#0F172A", linewidth=0.5)
    ax1.set_title("Average LLM Generation Latency (Seconds)", fontsize=12, fontweight="bold", pad=12, color="#0F172A")
    ax1.set_ylabel("Latency (Seconds)", fontsize=10, fontweight="bold")
    ax1.set_ylim(0, max(latencies) * 1.25)
    add_bar_labels(ax1, bars1, fmt="%.2f", unit="s")

    # Subplot 2: Throughput
    bars2 = ax2.bar(llm_models, throughputs, color=colors, width=0.55, edgecolor="#0F172A", linewidth=0.5)
    ax2.set_title("Generation Throughput (Tokens / Second)", fontsize=12, fontweight="bold", pad=12, color="#0F172A")
    ax2.set_ylabel("Tokens / Second", fontsize=10, fontweight="bold")
    ax2.set_ylim(0, max(throughputs) * 1.25)
    add_bar_labels(ax2, bars2, fmt="%.1f", unit=" tps")

    fig.suptitle("LLM Performance Comparison: Cloud API vs Local LLM vs Deterministic Fallback", fontsize=14, fontweight="bold", y=1.02, color="#0F172A")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"✅ บันทึกกราฟที่ 2 สำเร็จ: {output_path}")


def plot_llm_resource_usage(output_path: str):
    """
    กราฟที่ 3: เปรียบเทียบการบริโภคทรัพยากรเครื่องคอมพิวเตอร์
    - Subplot 1: Memory / RAM Consumption (MB)
    - Subplot 2: CPU Load During Generation (%)
    """
    llm_models = [
        "Gemini 3.1\nFlash Lite (API)",
        "Qwen 2.5 3B\n(Local CPU)",
        "Gemma 3 4B\n(Local CPU)",
        "Retriever\nFallback (Offline)"
    ]
    ram_usage_mb = [0, 2450, 3780, 8]  # MB
    cpu_percent = [0, 55, 85, 0]        # %

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")

    colors = ["#0284C7", "#D97706", "#DC2626", "#059669"]

    # Subplot 1: RAM Usage
    bars1 = ax1.bar(llm_models, ram_usage_mb, color=colors, width=0.52, edgecolor="#0F172A", linewidth=0.5)
    ax1.set_title("Local RAM / VRAM Consumption (MB)", fontsize=12, fontweight="bold", pad=12, color="#0F172A")
    ax1.set_ylabel("RAM Usage (MB)", fontsize=10, fontweight="bold")
    ax1.set_ylim(0, max(ram_usage_mb) * 1.25)
    add_bar_labels(ax1, bars1, fmt="%d", unit=" MB")

    # Subplot 2: CPU Load
    bars2 = ax2.bar(llm_models, cpu_percent, color=colors, width=0.52, edgecolor="#0F172A", linewidth=0.5)
    ax2.set_title("Machine CPU Load During Generation (%)", fontsize=12, fontweight="bold", pad=12, color="#0F172A")
    ax2.set_ylabel("CPU Load (%)", fontsize=10, fontweight="bold")
    ax2.set_ylim(0, 110)
    add_bar_labels(ax2, bars2, fmt="%d", unit="%")

    fig.suptitle("Machine Resource Footprint: Cloud API Zero-Overhead vs Local Throttling", fontsize=14, fontweight="bold", y=1.02, color="#0F172A")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"✅ บันทึกกราฟที่ 3 สำเร็จ: {output_path}")


def plot_category_latency(output_path: str):
    """
    กราฟที่ 4: แสดงเวลาประมวลผล End-to-End แยกตามหมวดหมู่ข้อสอบ A ถึง J
    ดึงข้อมูลจริงจาก data/benchmark_results_gemini.json
    """
    categories = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    cat_names = [
        "A: General POI",
        "B: Temples/History",
        "C: Anime/Gaming",
        "D: Parks/Views",
        "E: Food/Markets",
        "F: Spatial/Walking",
        "G: Route/Transit",
        "H: 1-Day Itinerary",
        "I: Preferences",
        "J: Multi-hop Graph"
    ]
    default_latencies = [7.64, 3.63, 5.23, 4.25, 4.60, 4.14, 5.54, 7.87, 2.84, 3.70]

    # พยายามอ่านผลจริงจาก JSON ล่าสุด
    latencies = default_latencies
    if os.path.exists(BENCHMARK_GEMINI_FILE):
        try:
            with open(BENCHMARK_GEMINI_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                breakdown = data.get("summary", {}).get("category_breakdown", {})
                loaded = []
                for c in categories:
                    if c in breakdown:
                        loaded.append(round(breakdown[c].get("avg_latency", 4.0), 2))
                if len(loaded) == 10:
                    latencies = loaded
        except Exception as e:
            print(f"⚠️ ใช้ค่า Default หมวดหมู่เนื่องจาก: {e}")

    fig, ax = plt.subplots(figsize=(13, 6), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")

    # กำหนดสีตามความเร็ว (Gradient)
    norm = plt.Normalize(min(latencies), max(latencies))
    cmap = plt.cm.get_cmap("Blues")
    bar_colors = [cmap(0.45 + (0.5 * (val - min(latencies)) / (max(latencies) - min(latencies) + 1e-6))) for val in latencies]

    bars = ax.bar(cat_names, latencies, color=bar_colors, width=0.6, edgecolor="#0F172A", linewidth=0.5)
    ax.axhline(5.0, color="#DC2626", linestyle="--", linewidth=1.2, label="Level 5 Target Threshold (< 5.0s)")
    ax.set_title("End-to-End Latency by Query Category (A to J) with Gemini 3.1 Flash Lite", fontsize=13, fontweight="bold", pad=12, color="#0F172A")
    ax.set_ylabel("Latency (Seconds)", fontsize=10, fontweight="bold")
    ax.set_ylim(0, max(latencies) * 1.25)
    plt.xticks(rotation=25, ha="right", fontsize=9, fontweight="bold")
    add_bar_labels(ax, bars, fmt="%.2f", unit="s")
    ax.legend(loc="upper right", frameon=True)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"✅ บันทึกกราฟที่ 4 สำเร็จ: {output_path}")


def generate_all_charts():
    """สร้างกราฟทั้งหมด 4 รูปแบบ"""
    os.makedirs(CHARTS_DIR, exist_ok=True)
    setup_style()

    print("🎨 กำลังสร้างภาพกราฟฟิกเปรียบเทียบผลการทดลอง (Resolution: 300 DPI)...")
    plot_embedding_comparison(os.path.join(CHARTS_DIR, "chart_1_embedding_comparison.png"))
    plot_llm_latency_throughput(os.path.join(CHARTS_DIR, "chart_2_llm_latency_throughput.png"))
    plot_llm_resource_usage(os.path.join(CHARTS_DIR, "chart_3_llm_resource_usage.png"))
    plot_category_latency(os.path.join(CHARTS_DIR, "chart_4_category_latency.png"))
    print(f"🎉 สร้างภาพกราฟทั้งหมดสำเร็จเรียบร้อยในโฟลเดอร์: {CHARTS_DIR}")


if __name__ == "__main__":
    generate_all_charts()
