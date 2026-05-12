# Judge Bias Report

## Quantified Bias Table

| Bias | Measurement | Result | Interpretation |
|---|---:|---:|---|
| Position bias | A wins when listed first | 6/30 (20.0%) | Below 55%, swap-and-average reduced position bias. |
| Length bias | B wins when B is longer | 18/30 (60.0%) | Longer, more explicit answers are preferred, so conciseness must stay in the rubric. |
| Tie rate | Final ties after swap | 12/30 | Ties preserve uncertainty instead of forcing noisy preferences. |

## Chart

```text
Position A wins: ######........................ 6/30
Length B wins:   ##################............ 18/30
Ties:            ############..................
```

## Mitigation

Use swap-and-average for every pairwise judgment, keep the concise/helpful rubric dimension in absolute scoring, and route low-confidence ties to human calibration.
