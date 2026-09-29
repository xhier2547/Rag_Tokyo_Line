"""Normalize and validate the per-question ground truth benchmark.

The benchmark remains a checked-in JSON artifact.  This script only applies
explicit reviewer-approved corrections and derives valid chunk IDs from the
curated entity IDs, so the rewrite is deterministic and reproducible.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_PATH = ROOT / "data" / "benchmark_100_questions.json"
CHUNKS_PATH = ROOT / "data" / "processed" / "documents_chunks.json"


ENTITY_ALIASES = {
    "P_HAMARIKYU": "P_HAMARIKYU_GARDENS",
    "P_TEAMLAB": "P_TEAMLAB_PLANETS",
    "P_TOKYO_DOME": "P_TOKYO_DOME_CITY",
    "P_OMOTESANDO": "P_OMOTESANDO_HILLS",
    "P_TAKESHITA": "P_TAKESHITA_STREET",
}


# Corrections where the previous category-level ground truth did not answer
# the actual question.  IDs not listed here retain the already curated values.
ENTITY_OVERRIDES = {
    8: ["P_HAMARIKYU_GARDENS", "P_TEAMLAB_PLANETS", "P_TOKYO_DOME_CITY", "P_OMOTESANDO_HILLS"],
    13: ["P_MEIJI_JINGU"],
    14: ["P_SENSOJI", "P_MEIJI_JINGU"],
    15: ["P_SENSOJI", "P_IMPERIAL_PALACE"],
    16: ["P_SENSOJI", "P_MEIJI_JINGU", "P_IMPERIAL_PALACE"],
    17: ["P_UENO_PARK"],
    18: ["P_HAMARIKYU_GARDENS", "P_SHINJUKU_GYOEN", "P_IMPERIAL_PALACE"],
    20: ["P_SENSOJI"],
    23: ["P_ODAIBA_GUNDAM"],
    25: ["P_ODAIBA_GUNDAM", "P_TEAMLAB_PLANETS"],
    28: ["P_AKIHABARA_ELECTRIC", "P_ODAIBA_GUNDAM", "P_TEAMLAB_PLANETS"],
    29: ["P_TEAMLAB_PLANETS", "P_AKIHABARA_ELECTRIC"],
    35: ["P_TOKYO_SKYTREE", "P_TOKYO_TOWER", "P_ROPPONGI_HILLS"],
    37: ["P_SHIBUYA_CROSSING", "P_ODAIBA_GUNDAM"],
    38: ["P_TOKYO_TOWER", "P_TOKYO_SKYTREE", "P_ROPPONGI_HILLS"],
    39: ["P_SHINJUKU_GYOEN", "P_UENO_PARK", "P_HAMARIKYU_GARDENS"],
    44: ["P_TSUKIJI_OUTER", "P_TOYOSU_MARKET"],
    48: ["P_TSUKIJI_OUTER", "P_SENSOJI"],
    49: ["P_HAMARIKYU_GARDENS", "P_GINZA_SIX"],
    53: ["P_MEIJI_JINGU", "P_TAKESHITA_STREET", "P_OMOTESANDO_HILLS"],
    57: ["P_TOKYO_SKYTREE", "P_SENSOJI"],
    69: ["P_UENO_PARK", "P_AKIHABARA_ELECTRIC", "P_SHIBUYA_CROSSING", "P_MEIJI_JINGU", "P_TOKYO_TOWER"],
    75: ["P_SHIBUYA_CROSSING", "P_TAKESHITA_STREET", "P_SHINJUKU_GYOEN"],
    91: ["P_SENSOJI"],
    95: ["P_SHINJUKU_GYOEN", "P_MEIJI_JINGU", "P_TAKESHITA_STREET", "P_OMOTESANDO_HILLS"],
}


def curate() -> None:
    questions = json.loads(BENCHMARK_PATH.read_text(encoding="utf-8"))
    chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    chunks_by_entity: dict[str, list[str]] = {}
    for chunk in chunks:
        chunks_by_entity.setdefault(chunk["place_id"], []).append(chunk["chunk_id"])

    for question in questions:
        qid = question["id"]
        entities = ENTITY_OVERRIDES.get(qid, question["ground_truth_entities"])
        normalized = []
        for entity in entities:
            entity = ENTITY_ALIASES.get(entity, entity)
            if entity not in normalized:
                normalized.append(entity)

        missing = [entity for entity in normalized if entity not in chunks_by_entity]
        if missing:
            raise ValueError(f"Q{qid} references entities absent from the knowledge base: {missing}")

        question["ground_truth_entities"] = normalized
        question["ground_truth_chunks"] = [
            chunk_id
            for entity in normalized
            for chunk_id in chunks_by_entity[entity]
        ]

    BENCHMARK_PATH.write_text(
        json.dumps(questions, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    curate()
