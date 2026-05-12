# Demo Checklist

Check these before submitting the video.

## Required Lab Demo

- [ ] Opened `README.md` and showed Results Summary.
- [ ] Ran `python scripts/run_eval.py`.
- [ ] Showed `phase-a/ragas_summary.json`.
- [ ] Showed `phase-a/failure_analysis.md`.
- [ ] Showed OpenAI live judge files:
  - [ ] `live/openai_pairwise_results.csv`
  - [ ] `live/openai_absolute_scores.csv`
- [ ] Ran or showed `python scripts/live_api_smoke.py` output.
- [ ] Showed guardrail result files:
  - [ ] `phase-c/pii_test_results.csv`
  - [ ] `phase-c/adversarial_test_results.csv`
  - [ ] `phase-c/output_guard_test_results.csv`
- [ ] Ran `python phase-c/full_pipeline.py --n 100`.
- [ ] Showed `phase-c/latency_benchmark.csv`.
- [ ] Showed `phase-d/blueprint.md`.
- [ ] Showed `bonus/README.md`.

## Safety

- [ ] Did not open `.env` during recording.
- [ ] Did not show API keys in terminal.
- [ ] `.env` is listed in `.gitignore`.
- [ ] `.env.example` exists for reproducibility.

## Submission

- [ ] Save video in `demo/` if the platform accepts video files.
- [ ] If the video is large, upload to YouTube/Loom unlisted and paste the link in root `README.md`.
- [ ] If storing locally, recommended filename: `demo/demo-video.mp4`.
- [ ] Final test passed: `python -m unittest discover -s tests`.
- [ ] Eval gate passed: `python scripts/run_eval.py`.
