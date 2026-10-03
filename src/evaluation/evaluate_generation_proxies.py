"""Auditable automatic proxies for answer relevance and citation validity.

These metrics do not claim factual faithfulness.  They screen saved outputs and
identify answers that need human review.
"""

import json
import re
from pathlib import Path
from statistics import mean

from src.vector.bm25_store import tokenize_corpus_text

BASE_DIR = Path(__file__).resolve().parents[2]


def _normalize(text: str) -> str:
    return re.sub(r"[^\w\u0e00-\u0e7f]+", " ", text.lower()).strip()


def _known_sources() -> list[str]:
    chunks = json.loads((BASE_DIR / "data/processed/documents_chunks.json").read_text(encoding="utf-8"))
    values = set()
    for chunk in chunks:
        for key in ("title", "place_id", "nearest_station"):
            value = _normalize(str(chunk.get(key, "")))
            if value:
                values.add(value)
    return sorted(values)


def citation_is_known(citation: str, known_sources: list[str]) -> bool:
    normalized = _normalize(citation)
    return any(
        len(source) >= 3 and (source in normalized or normalized in source)
        for source in known_sources
    )


def lexical_answer_relevance(query: str, answer: str) -> float:
    query_tokens = {token for token in tokenize_corpus_text(query) if len(token) > 1}
    answer_tokens = set(tokenize_corpus_text(answer))
    if not query_tokens:
        return 0.0
    return len(query_tokens & answer_tokens) / len(query_tokens)


def evaluate(input_path: str, output_path: str) -> dict:
    source = json.loads((BASE_DIR / input_path).read_text(encoding="utf-8"))
    known_sources = _known_sources()
    rows = []
    for item in source.get("details", []):
        citations = item.get("citations", [])
        checks = [citation_is_known(citation, known_sources) for citation in citations]
        rows.append({
            "question_id": item.get("question_id"),
            "category": item.get("category"),
            "query": item.get("query", ""),
            "citation_count": len(citations),
            "known_citation_count": sum(checks),
            "citation_validity_proxy": round(sum(checks) / len(checks), 4) if checks else 0.0,
            "lexical_answer_relevance_proxy": round(
                lexical_answer_relevance(item.get("query", ""), item.get("answer", "")), 4
            ),
            "needs_human_review": not citations or not all(checks),
        })

    cited_rows = [row for row in rows if row["citation_count"] > 0]
    payload = {
        "metadata": {
            "source": input_path,
            "items": len(rows),
            "limitations": (
                "Automatic screening proxies only. Citation validity checks whether a named source exists; "
                "lexical relevance measures token overlap. Neither metric proves factual faithfulness."
            ),
        },
        "summary": {
            "citation_presence_rate": round(len(cited_rows) / len(rows), 4) if rows else 0.0,
            "avg_citation_validity_proxy_when_present": round(
                mean(row["citation_validity_proxy"] for row in cited_rows), 4
            ) if cited_rows else 0.0,
            "avg_lexical_answer_relevance_proxy": round(mean(row["lexical_answer_relevance_proxy"] for row in rows), 4) if rows else 0.0,
            "items_needing_human_review": sum(row["needs_human_review"] for row in rows),
        },
        "details": rows,
    }
    target = BASE_DIR / output_path
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = evaluate(
        "data/benchmark_results_comprehensive.json",
        "data/generation_quality_proxies.json",
    )
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))

