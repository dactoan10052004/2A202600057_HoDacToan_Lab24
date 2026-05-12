"""Streamlit dashboard for Lab 24 eval and guardrail artifacts."""

from __future__ import annotations

import csv
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parents[1]


st.set_page_config(page_title="Lab 24 Eval Dashboard", layout="wide")
st.title("Lab 24 Evaluation and Guardrail Dashboard")

summary_path = ROOT / "phase-a" / "ragas_summary.json"
ragas_path = ROOT / "phase-a" / "ragas_results.csv"
latency_path = ROOT / "phase-c" / "latency_benchmark.csv"
adversarial_path = ROOT / "phase-c" / "adversarial_test_results.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

if summary_path.exists():
    st.subheader("RAGAS Summary")
    st.json(summary_path.read_text(encoding="utf-8"))

left, right = st.columns(2)
with left:
    st.subheader("RAGAS Results")
    if ragas_path.exists():
        st.dataframe(read_csv(ragas_path), use_container_width=True)
        st.caption("Open the CSV artifact for full row-level metric inspection.")

with right:
    st.subheader("Guardrail Latency")
    if latency_path.exists():
        st.dataframe(read_csv(latency_path), use_container_width=True)
        st.caption("Benchmark contains 100 guarded requests with L1/L2/L3 timings.")

st.subheader("Adversarial Defense")
if adversarial_path.exists():
    st.dataframe(read_csv(adversarial_path), use_container_width=True)
