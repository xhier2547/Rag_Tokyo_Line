"""Measure retrieval latency across repeated full benchmark runs.

The output reports sample standard deviation and a 95% confidence interval for
the mean. Accuracy metrics are retained per run so unexpected drift is visible.
"""

import argparse
import json
import statistics
import tempfile
from pathlib import Path

from src.evaluation.run_comprehensive_eval import load_benchmark, run_ablation_study


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--benchmark-file", default="data/benchmark_100_questions.json")
    parser.add_argument("--output", default="data/retrieval_latency_repeated_runs.json")
    args = parser.parse_args()
    if args.runs < 2:
        raise ValueError("--runs must be at least 2 to calculate sample variability")

    questions = load_benchmark(args.benchmark_file)
    runs = []
    with tempfile.TemporaryDirectory(prefix="tokyo-rag-latency-") as temp_dir:
        for run_number in range(1, args.runs + 1):
            raw_path = str(Path(temp_dir) / f"run_{run_number}.json")
            summary = run_ablation_study(questions, raw_output_path=raw_path)
            runs.append({"run": run_number, "summary": summary})

    aggregate = {}
    for mode in ("dense_only", "graph_only", "hybrid_rag"):
        values = [run["summary"][mode]["avg_latency_ms"] for run in runs]
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        # Student's t is appropriate here because the number of runs is small.
        t_critical_95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
                         6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}.get(len(values) - 1, 1.96)
        margin = t_critical_95 * stdev / (len(values) ** 0.5)
        aggregate[mode] = {
            "runs": len(values),
            "mean_latency_ms": round(mean, 3),
            "sample_stdev_ms": round(stdev, 3),
            "ci95_mean_latency_ms": [round(mean - margin, 3), round(mean + margin, 3)],
            "min_latency_ms": round(min(values), 3),
            "max_latency_ms": round(max(values), 3),
        }

    output = {
        "benchmark_file": args.benchmark_file,
        "questions_per_run": len(questions),
        "method": "Independent full retrieval runs; two-sided 95% Student's t CI over run means.",
        "runs": runs,
        "aggregate": aggregate,
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, ensure_ascii=False, indent=2))
    print(f"Saved repeated-run latency evidence: {output_path}")


if __name__ == "__main__":
    main()
