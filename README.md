# Lab 24 - Full Evaluation & Guardrail System

## Overview

This repo implements an offline-first Lab 24 evaluation and guardrail system for a RAG pipeline. It includes synthetic test set generation, RAGAS-style metrics, failure clustering, pairwise and absolute LLM-as-judge artifacts, human calibration with Cohen's kappa, input/output guardrails, full-stack latency benchmarking, and a production blueprint. The code is deterministic so it can run without paid API keys, while keeping adapter points for replacing the mock RAG and offline guard with real Day 18 RAG, RAGAS, Presidio, OpenAI, and Llama Guard 3.

## Setup

```bash
copy .env.example .env
python scripts/generate_artifacts.py
python bonus/cross_judge_protocol.py
python bonus/selfcheckgpt.py
python bonus/semantic_entropy.py
python -m unittest discover -s tests
python scripts/run_eval.py
```

The default repo is offline and does not require an LLM API key. For a live/high-score run, install `requirements-live.txt`, fill `.env`, set `LAB24_MODE=live`, and run:

```bash
python scripts/check_env.py
python scripts/live_api_smoke.py
python scripts/run_live_judge.py --limit 10
```

Then replace `rag_pipeline_async` in `phase-c/full_pipeline.py` with the Day 18 RAG call.

Recommended live keys:

- `OPENAI_API_KEY`: RAGAS synthetic generation, RAGAS metrics, and LLM judge.
- `GROQ_API_KEY`: hosted Prompt Guard 2 for live prompt-injection detection. Llama Guard 3 is deprecated on current Groq docs, so this repo keeps the Lab 24 Llama Guard path as an offline-compatible baseline.
- `HUGGINGFACEHUB_API_TOKEN`: gated Hugging Face model downloads.
- `LANGSMITH_API_KEY` or `LANGFUSE_*`: optional eval tracing.

## Results Summary

### Phase A (RAGAS)

- Test set: 50 questions (25 simple, 13 reasoning, 12 multi-context).
- Faithfulness: 0.791 | AR: 0.769 | CP: 0.666 | CR: 0.708
- Total eval cost: $0.00 for offline baseline; estimate $3-5 for live GPT-4o-mini generation/evaluation.
- Main failure clusters: multi-hop retrieval, retrieval precision, and safety-policy ambiguity.

### Phase B (LLM-Judge)

- Pairwise judging runs 30 questions with swap-and-average mitigation.
- Cohen's kappa vs human labels: see `phase-b/kappa_output.txt`.
- Bias report quantifies position bias, length bias, and tie rate in `phase-b/judge_bias_report.md`.

### Phase C (Guardrails)

- PII detection test: 100% correctness across PII and edge cases.
- Topic validator: 100% accuracy on 20 inputs with graceful refusal.
- Adversarial defense: 85% block rate across 20 jailbreak, roleplay, split, encoding, and indirect injection attacks.
- Output guard: 100% unsafe detection, 0% false positive rate on 10 unsafe + 10 safe outputs.
- Latency benchmark: 100 requests, L1 P95 1.06ms and L3 P95 0.66ms.

### Phase D (Blueprint)

See `phase-d/blueprint.md` for SLOs, 4-layer architecture, incident playbooks, and monthly cost projection.

### Bonus

- Cross-judge protocol: 3 judge profiles with aggregate voting.
- SelfCheckGPT-style hallucination detection: consistency scoring over sampled answers.
- Semantic entropy: answer-cluster entropy for uncertainty detection.
- Prompt Guard-style classifier: injection patterns and encoded attack checks in `InjectionGuard`.
- Eval dashboard: `streamlit run dashboard/app.py`.
- Blog post draft: `blog_post.md`.

### Live API Evidence

- OpenAI smoke: `live/live_api_smoke.json`.
- OpenAI live pairwise judge sample: `live/openai_pairwise_results.csv`.
- OpenAI live absolute scoring sample: `live/openai_absolute_scores.csv`.
- Groq live Prompt Guard 2 smoke: recorded in `live/live_api_smoke.json`.

## Lessons Learned

Evaluation and guardrails need to be treated as one system. RAGAS-style metrics catch regressions after generation, while input and output guardrails reduce harmful or out-of-scope interactions before they reach users.

Pairwise judging is useful only when bias is measured. Swap-and-average, human calibration, and explicit tie handling make the judge safer to use in monitoring.

The most practical production risk is latency overhead. This repo records per-layer timing so the team can decide whether to optimize PII redaction, topic validation, output safety, or the RAG call itself.

## Demo Video

Record a 5-minute demo showing: eval gate on 5 questions, pairwise judge, 3 adversarial blocks, and latency benchmark output. Add the YouTube/Loom link here before submission.
