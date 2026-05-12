"""Bonus: SelfCheckGPT-style consistency detector.

This is an offline implementation: it compares multiple sampled answer variants
and flags hallucination risk when the answers disagree semantically.
"""

from __future__ import annotations

import csv
import itertools
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def tokens(text: str) -> set[str]:
    stop = {"the", "a", "an", "and", "or", "to", "of", "in", "for", "with", "is"}
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in stop}


def jaccard(a: str, b: str) -> float:
    ta = tokens(a)
    tb = tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def disagreement(samples: list[str]) -> float:
    pairs = list(itertools.combinations(samples, 2))
    if not pairs:
        return 0.0
    return 1 - sum(jaccard(a, b) for a, b in pairs) / len(pairs)


def main() -> None:
    examples = [
        {
            "question_id": 1,
            "question": "What does faithfulness measure?",
            "samples": [
                "Faithfulness measures whether the answer is supported by retrieved context.",
                "It checks that generated claims are grounded in the retrieved passages.",
                "Faithfulness is about context-supported answers, not style.",
            ],
        },
        {
            "question_id": 2,
            "question": "What is the latency target?",
            "samples": [
                "The guarded pipeline should keep P95 latency under 2.5 seconds.",
                "The target is P95 below 2.5 seconds with alerts above 3 seconds.",
                "The monthly cost target is 386 dollars.",
            ],
        },
        {
            "question_id": 3,
            "question": "What does Cohen's kappa measure?",
            "samples": [
                "Kappa measures human and judge agreement beyond chance.",
                "It quantifies agreement after correcting for chance agreement.",
                "It is used to calibrate LLM judge labels against human labels.",
            ],
        },
    ]
    rows = []
    for example in examples:
        risk = disagreement(example["samples"])
        rows.append({
            "question_id": example["question_id"],
            "question": example["question"],
            "sample_count": len(example["samples"]),
            "disagreement_score": round(risk, 3),
            "hallucination_risk": "high" if risk > 0.72 else "medium" if risk > 0.55 else "low",
        })

    out = ROOT / "bonus" / "selfcheckgpt_results.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
