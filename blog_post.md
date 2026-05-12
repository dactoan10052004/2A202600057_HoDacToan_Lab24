# What I Learned Building a Full Evaluation and Guardrail Stack

Lab 24 made one thing very clear: a RAG demo is not a production AI system. A demo only proves that one happy path can produce an answer. A production system needs evaluation, guardrails, calibration, monitoring, and a way to debug failures after the model changes.

The first lesson was that RAGAS metrics should be read together, not one by one. Faithfulness tells me whether the answer is grounded, answer relevancy tells me whether it responds to the question, and context precision/recall show whether retrieval is helping or hurting. The failure analysis was the most useful part because bottom-10 clustering turns abstract scores into engineering actions like increasing `top_k`, adding reranking, or indexing a policy corpus.

The second lesson was that LLM-as-judge is powerful but biased. A single judge result is easy to over-trust. Swap-and-average, cross-judge voting, human calibration, and Cohen's kappa make the signal much more credible. Ties are not failures; they are useful uncertainty.

The third lesson was that guardrails need latency budgets. PII redaction, topic validation, injection detection, output safety, and audit logging all add value, but only if the request still feels responsive. Measuring L1/L2/L3 separately makes optimization obvious.

My production takeaway is simple: ship eval and guardrails as part of the product, not as a notebook afterthought.
