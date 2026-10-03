"""Create deterministic, category-stratified development and test splits."""

import json
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
SOURCE = BASE_DIR / "data" / "benchmark_100_questions.json"
DEV_OUTPUT = BASE_DIR / "data" / "benchmark_dev_60.json"
TEST_OUTPUT = BASE_DIR / "data" / "benchmark_test_40.json"


def create_splits() -> tuple[list, list]:
    questions = json.loads(SOURCE.read_text(encoding="utf-8"))
    grouped = defaultdict(list)
    for item in questions:
        grouped[item["category"]].append(item)

    dev, test = [], []
    for category in sorted(grouped):
        items = sorted(grouped[category], key=lambda item: item["id"])
        if len(items) != 10:
            raise ValueError(f"Category {category} must contain 10 questions, found {len(items)}")
        dev.extend(items[:6])
        test.extend(items[6:])

    DEV_OUTPUT.write_text(json.dumps(dev, ensure_ascii=False, indent=2), encoding="utf-8")
    TEST_OUTPUT.write_text(json.dumps(test, ensure_ascii=False, indent=2), encoding="utf-8")
    return dev, test


if __name__ == "__main__":
    dev_items, test_items = create_splits()
    print(f"Created development={len(dev_items)} and test={len(test_items)} questions")

