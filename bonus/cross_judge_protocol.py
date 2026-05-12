"""Bonus: cross-judge protocol with 3 deterministic judge profiles."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def score_answer(answer: str, profile: str) -> float:
    length = len(answer)
    cites_metric = any(term in answer.lower() for term in ["faithfulness", "context", "guardrail", "kappa", "latency"])
    if profile == "accuracy_first":
        return (2.0 if cites_metric else 0.5) + min(length, 260) / 260
    if profile == "concise_first":
        return (2.0 if cites_metric else 0.5) + max(0, 220 - length) / 220
    if profile == "helpfulness_first":
        return (2.0 if cites_metric else 0.5) + answer.count(".") * 0.2 + min(length, 320) / 320
    raise ValueError(profile)


def judge_pair(answer_a: str, answer_b: str, profile: str) -> str:
    score_a = score_answer(answer_a, profile)
    score_b = score_answer(answer_b, profile)
    if abs(score_a - score_b) < 0.12:
        return "tie"
    return "A" if score_a > score_b else "B"


def aggregate(votes: list[str]) -> tuple[str, float]:
    counts = Counter(votes)
    winner, count = counts.most_common(1)[0]
    if winner == "tie" and len(counts) > 1:
        non_tie = [(label, value) for label, value in counts.items() if label != "tie"]
        if non_tie and non_tie[0][1] == count:
            winner = non_tie[0][0]
    return winner, count / len(votes)


def main() -> None:
    input_path = ROOT / "phase-b" / "pairwise_results.csv"
    output_path = ROOT / "bonus" / "cross_judge_results.csv"
    profiles = ["accuracy_first", "concise_first", "helpfulness_first"]
    with input_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))[:30]

    out_rows = []
    for row in rows:
        votes = [judge_pair(row["answer_a"], row["answer_b"], profile) for profile in profiles]
        winner, confidence = aggregate(votes)
        out_rows.append({
            "question_id": row["question_id"],
            "judge_accuracy_first": votes[0],
            "judge_concise_first": votes[1],
            "judge_helpfulness_first": votes[2],
            "aggregate_winner": winner,
            "agreement": round(confidence, 3),
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)


if __name__ == "__main__":
    main()
