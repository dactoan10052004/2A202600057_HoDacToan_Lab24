import csv
from collections import Counter


def cohen_kappa(human, judge):
    labels = sorted(set(human) | set(judge))
    observed = sum(1 for h, j in zip(human, judge) if h == j) / len(human)
    human_counts = Counter(human)
    judge_counts = Counter(judge)
    expected = sum((human_counts[label] / len(human)) * (judge_counts[label] / len(judge)) for label in labels)
    return 1.0 if expected == 1.0 else (observed - expected) / (1 - expected)


with open("phase-b/human_labels.csv", newline="", encoding="utf-8") as f:
    human = [row["human_winner"] for row in csv.DictReader(f)]
with open("phase-b/pairwise_results.csv", newline="", encoding="utf-8") as f:
    judge = [row["winner_after_swap"] for row in list(csv.DictReader(f))[:10]]

kappa = cohen_kappa(human, judge)
print(f"Cohen's kappa: {kappa:.3f}")
if kappa < 0.2:
    print("Slight agreement - not reliable")
elif kappa < 0.4:
    print("Fair agreement - still weak")
elif kappa < 0.6:
    print("Moderate agreement - usable for monitoring with caution")
elif kappa < 0.8:
    print("Substantial agreement - production-ready")
else:
    print("Almost perfect agreement")
