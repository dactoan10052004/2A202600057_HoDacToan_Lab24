"""Run a small live OpenAI judge pass over existing Lab 24 pairwise data."""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from pathlib import Path

from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]


PAIRWISE_PROMPT = """You are an impartial evaluator. Compare two answers to the same question.

Question: {question}
Answer A: {answer_a}
Answer B: {answer_b}

Rate based on factual accuracy, relevance, and conciseness.
Output JSON only: {{"winner":"A"|"B"|"tie","reason":"short reason"}}"""


ABSOLUTE_PROMPT = """Score the answer on 4 dimensions, each 1-5:
accuracy, relevance, conciseness, helpfulness.

Question: {question}
Answer: {answer}

Output JSON only:
{{"accuracy":int,"relevance":int,"conciseness":int,"helpfulness":int,"overall":float}}"""


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_json(text: str) -> dict[str, object]:
    cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"winner": "tie", "reason": f"parse_error: {cleaned[:80]}"}


def call_json(client: OpenAI, model: str, prompt: str, max_tokens: int = 160) -> tuple[dict[str, object], float]:
    start = time.perf_counter()
    response = client.responses.create(model=model, input=prompt, max_output_tokens=max_tokens)
    latency_ms = (time.perf_counter() - start) * 1000
    return parse_json(response.output_text), latency_ms


def flip_winner(winner: str) -> str:
    if winner == "A":
        return "B"
    if winner == "B":
        return "A"
    return "tie"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    with (ROOT / "phase-b" / "pairwise_results.csv").open(encoding="utf-8", newline="") as f:
        source_rows = list(csv.DictReader(f))[: args.limit]

    pairwise_rows: list[dict[str, object]] = []
    absolute_rows: list[dict[str, object]] = []
    for row in source_rows:
        run1, latency1 = call_json(
            client,
            model,
            PAIRWISE_PROMPT.format(question=row["question"], answer_a=row["answer_a"], answer_b=row["answer_b"]),
        )
        run2_raw, latency2 = call_json(
            client,
            model,
            PAIRWISE_PROMPT.format(question=row["question"], answer_a=row["answer_b"], answer_b=row["answer_a"]),
        )
        run2_winner = flip_winner(str(run2_raw.get("winner", "tie")))
        run1_winner = str(run1.get("winner", "tie"))
        final = run1_winner if run1_winner == run2_winner else "tie"
        pairwise_rows.append({
            "question_id": row["question_id"],
            "model": model,
            "run1_winner": run1_winner,
            "run2_winner_mapped": run2_winner,
            "winner_after_swap": final,
            "run1_reason": str(run1.get("reason", ""))[:200],
            "run2_reason": str(run2_raw.get("reason", ""))[:200],
            "latency_ms": round(latency1 + latency2, 2),
        })

        absolute, abs_latency = call_json(
            client,
            model,
            ABSOLUTE_PROMPT.format(question=row["question"], answer=row["answer_b"]),
        )
        dims = ["accuracy", "relevance", "conciseness", "helpfulness"]
        scores = {dim: int(absolute.get(dim, 3)) for dim in dims}
        overall = float(absolute.get("overall", sum(scores.values()) / 4))
        absolute_rows.append({
            "question_id": row["question_id"],
            "model": model,
            **scores,
            "overall": round(overall, 2),
            "latency_ms": round(abs_latency, 2),
        })

    out_dir = ROOT / "live"
    out_dir.mkdir(exist_ok=True)
    with (out_dir / "openai_pairwise_results.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(pairwise_rows[0].keys()))
        writer.writeheader()
        writer.writerows(pairwise_rows)
    with (out_dir / "openai_absolute_scores.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(absolute_rows[0].keys()))
        writer.writeheader()
        writer.writerows(absolute_rows)

    print(f"Wrote {len(pairwise_rows)} live pairwise rows and {len(absolute_rows)} absolute scores using {model}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
