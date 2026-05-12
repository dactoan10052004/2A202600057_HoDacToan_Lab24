"""Bonus: semantic entropy over answer clusters."""

from __future__ import annotations

import csv
import math
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def normalize_cluster(answer: str) -> str:
    text = answer.lower()
    if any(term in text for term in ["latency", "p95", "seconds"]):
        return "latency"
    if any(term in text for term in ["faithfulness", "grounded", "context"]):
        return "faithfulness"
    if any(term in text for term in ["kappa", "agreement", "chance"]):
        return "calibration"
    return re.sub(r"[^a-z0-9]+", "_", text)[:24]


def entropy(labels: list[str]) -> float:
    counts = Counter(labels)
    total = len(labels)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def main() -> None:
    samples = {
        1: [
            "Faithfulness checks whether answers are grounded in context.",
            "Grounding in retrieved context is measured by faithfulness.",
            "Faithfulness evaluates context support.",
        ],
        2: [
            "The P95 latency target is under 2.5 seconds.",
            "Alert when latency exceeds 3 seconds.",
            "The best metric is answer relevancy.",
        ],
        3: [
            "Kappa measures judge-human agreement beyond chance.",
            "Agreement corrected for chance is Cohen's kappa.",
            "Kappa is a calibration metric.",
        ],
    }
    rows = []
    for question_id, answers in samples.items():
        labels = [normalize_cluster(answer) for answer in answers]
        h = entropy(labels)
        rows.append({
            "question_id": question_id,
            "semantic_clusters": ";".join(labels),
            "semantic_entropy_bits": round(h, 3),
            "uncertainty": "high" if h > 0.9 else "low",
        })

    out = ROOT / "bonus" / "semantic_entropy_results.csv"
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
