# Lab 24 Demo Script

Use this script as the first screen in the demo if recording without voice.

## Goal

Show a complete Lab 24 Full Evaluation & Guardrail System:

1. Phase A: RAGAS-style evaluation gate and failure analysis.
2. Phase B: OpenAI live LLM-as-Judge evidence.
3. Phase C: Input/output guardrails, adversarial tests, and latency benchmark.
4. Phase D: Production blueprint with SLOs, architecture, playbooks, and cost.
5. Bonus: cross-judge, SelfCheckGPT-style consistency, semantic entropy, Prompt Guard, dashboard, and blog draft.

## Recording Flow

### 1. Overview

Open `README.md` and scroll through:

- `Results Summary`
- `Live API Evidence`
- `Bonus`

### 2. Phase A Evaluation

Run:

```bash
python scripts/run_eval.py
```

Open:

- `phase-a/ragas_summary.json`
- `phase-a/failure_analysis.md`

### 3. Phase B Live Judge

Open:

- `live/openai_pairwise_results.csv`
- `live/openai_absolute_scores.csv`

Optional live rerun:

```bash
python scripts/run_live_judge.py --limit 10
```

### 4. Phase C Guardrails

Run:

```bash
python scripts/live_api_smoke.py
```

Open:

- `phase-c/pii_test_results.csv`
- `phase-c/adversarial_test_results.csv`
- `phase-c/output_guard_test_results.csv`

### 5. Latency Benchmark

Run:

```bash
python phase-c/full_pipeline.py --n 100
```

Open:

- `phase-c/latency_benchmark.csv`

### 6. Production Blueprint

Open `phase-d/blueprint.md` and show:

- SLO table
- Mermaid architecture
- Alert playbooks
- Cost analysis

### 7. Bonus

Open `bonus/README.md` and show the bonus evidence table.

## Final Screen

Open `demo/checklist.md` and show that all required demo items are checked.
