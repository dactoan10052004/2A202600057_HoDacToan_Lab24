"""Full guardrail stack and latency benchmark for Lab 24."""

from __future__ import annotations

import argparse
import asyncio
import csv
import statistics
import time
from pathlib import Path

from input_guard import InjectionGuard, InputGuard, TopicGuard, refuse_response
from output_guard import OfflineLlamaGuard


ROOT = Path(__file__).resolve().parents[1]
PHASE_C = ROOT / "phase-c"


input_guard = InputGuard()
topic_guard = TopicGuard()
injection_guard = InjectionGuard()
output_guard = OfflineLlamaGuard()


async def rag_pipeline_async(question: str) -> str:
    """Mock Day 18 RAG adapter.

    Replace this function with the real retrieval + generation call. It is kept
    deterministic so the lab artifacts can be regenerated during CI.
    """

    await asyncio.sleep(0.001)
    lower = question.lower()
    if "faithfulness" in lower:
        return "Faithfulness measures whether the answer is supported by retrieved context."
    if "kappa" in lower:
        return "Cohen's kappa measures agreement between human labels and judge labels beyond chance."
    if "guardrail" in lower or "pii" in lower:
        return "The guardrail stack redacts PII, validates scope, blocks injections, checks output safety, and logs audit events."
    return "Lab 24 evaluates RAG systems using RAGAS metrics, LLM judging, safety guardrails, and production SLOs."


async def audit_log(user_input: str, answer: str, timings: dict[str, float]) -> None:
    await asyncio.sleep(0)


async def guarded_pipeline(user_input: str) -> tuple[str, dict[str, float]]:
    timings: dict[str, float] = {}

    t0 = time.perf_counter()
    pii_task = asyncio.create_task(input_guard.sanitize_async(user_input))
    topic_task = asyncio.create_task(topic_guard.check_async(user_input))
    injection_task = asyncio.create_task(injection_guard.check_async(user_input))

    sanitized, pii_latency, pii_found = await pii_task
    topic_ok, topic_reason = await topic_task
    injection_result = await injection_task
    timings["L1"] = (time.perf_counter() - t0) * 1000
    timings["pii"] = pii_latency

    if not topic_ok:
        return refuse_response(topic_reason), timings
    if not injection_result.ok:
        return refuse_response(injection_result.reason), timings

    t0 = time.perf_counter()
    answer = await rag_pipeline_async(sanitized)
    timings["L2"] = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    safety = await output_guard.check_async(sanitized, answer)
    timings["L3"] = (time.perf_counter() - t0) * 1000

    if not safety.is_safe:
        return refuse_response(safety.raw_result), timings

    asyncio.create_task(audit_log(user_input, answer, timings))
    return answer, timings


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = (len(sorted_values) - 1) * (p / 100)
    lower = int(index)
    upper = min(lower + 1, len(sorted_values) - 1)
    if lower == upper:
        return sorted_values[lower]
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * (index - lower)


def load_test_queries(n: int = 100) -> list[str]:
    seeds = [
        "How do I interpret RAGAS faithfulness for Lab 24?",
        "What does context recall mean in a RAG evaluation?",
        "How should I measure guardrail latency overhead?",
        "Explain Cohen's kappa for LLM judge calibration.",
        "Can PII redaction remove phone 0912345678 before retrieval?",
        "What SLO should monitor answer relevancy?",
        "How does swap-and-average reduce position bias?",
        "What should the audit log store for guardrail decisions?",
    ]
    return [seeds[i % len(seeds)] for i in range(n)]


async def benchmark(n: int = 100) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for idx, query in enumerate(load_test_queries(n), start=1):
        start = time.perf_counter()
        answer, timings = await guarded_pipeline(query)
        baseline_start = time.perf_counter()
        await rag_pipeline_async(query)
        baseline_ms = (time.perf_counter() - baseline_start) * 1000
        total_ms = (time.perf_counter() - start) * 1000
        rows.append({
            "request_id": idx,
            "L1_ms": round(timings.get("L1", 0.0), 3),
            "L2_ms": round(timings.get("L2", 0.0), 3),
            "L3_ms": round(timings.get("L3", 0.0), 3),
            "total_ms": round(total_ms, 3),
            "baseline_ms": round(baseline_ms, 3),
            "overhead_ms": round(max(total_ms - baseline_ms, 0.0), 3),
            "answer_status": "refused" if answer.startswith("I cannot") else "answered",
        })
    return rows


def summarize(rows: list[dict[str, float | str]]) -> dict[str, dict[str, float]]:
    summary: dict[str, dict[str, float]] = {}
    for column in ["L1_ms", "L2_ms", "L3_ms", "total_ms", "baseline_ms", "overhead_ms"]:
        values = [float(row[column]) for row in rows]
        summary[column] = {
            "p50": round(statistics.median(values), 3),
            "p95": round(percentile(values, 95), 3),
            "p99": round(percentile(values, 99), 3),
        }
    return summary


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument("--out", default=str(PHASE_C / "latency_benchmark.csv"))
    args = parser.parse_args()

    rows = await benchmark(args.n)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(summarize(rows))


if __name__ == "__main__":
    asyncio.run(main())
