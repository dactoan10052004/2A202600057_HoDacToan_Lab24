"""CI gate for Lab 24 evaluation metrics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DEFAULT_THRESHOLDS = {
    "faithfulness": 0.70,
    "answer_relevancy": 0.70,
    "context_precision": 0.60,
    "context_recall": 0.60,
}


def parse_threshold(raw: str) -> tuple[str, float]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError("Threshold must use metric=value format")
    metric, value = raw.split("=", 1)
    return metric.strip(), float(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", default="phase-a/ragas_summary.json")
    parser.add_argument("--threshold", action="append", type=parse_threshold, default=[])
    args = parser.parse_args()

    thresholds = DEFAULT_THRESHOLDS.copy()
    thresholds.update(dict(args.threshold))

    summary_path = Path(args.summary)
    if not summary_path.exists():
        print(f"Missing summary file: {summary_path}", file=sys.stderr)
        return 1

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    failures = []
    for metric, threshold in thresholds.items():
        value = float(summary.get(metric, 0.0))
        print(f"{metric}: {value:.3f} (threshold {threshold:.3f})")
        if value < threshold:
            failures.append((metric, value, threshold))

    if failures:
        for metric, value, threshold in failures:
            print(f"FAIL: {metric}={value:.3f} < {threshold:.3f}", file=sys.stderr)
        return 1
    print("PASS: all evaluation thresholds met")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
