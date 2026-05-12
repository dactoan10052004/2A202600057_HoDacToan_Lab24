# Failure Cluster Analysis

## Bottom 10 Questions

| # | Question (truncated) | Type | F | AR | CP | CR | Avg | Cluster |
|---|---|---|---:|---:|---:|---:|---:|---|
| 1 | How do refuse rate and the guardrail stack interact in the production  | multi_context | 0.535 | 0.544 | 0.39 | 0.445 | 0.479 | C1 |
| 2 | How do synthetic test generation and the guardrail stack interact in t | multi_context | 0.52 | 0.562 | 0.39 | 0.495 | 0.492 | C1 |
| 3 | How do reranking and the guardrail stack interact in the production bl | multi_context | 0.58 | 0.508 | 0.45 | 0.52 | 0.514 | C1 |
| 4 | Why should topic validation be monitored together with guardrail laten | reasoning | 0.56 | 0.548 | 0.45 | 0.51 | 0.517 | C2 |
| 5 | How do failure clustering and the guardrail stack interact in the prod | multi_context | 0.595 | 0.58 | 0.45 | 0.47 | 0.524 | C1 |
| 6 | Why should alert playbooks be monitored together with guardrail latenc | reasoning | 0.605 | 0.566 | 0.49 | 0.51 | 0.543 | C2 |
| 7 | Why should position bias be monitored together with guardrail latency? | reasoning | 0.605 | 0.602 | 0.51 | 0.485 | 0.55 | C2 |
| 8 | How do audit logs and the guardrail stack interact in the production b | multi_context | 0.73 | 0.688 | 0.61 | 0.625 | 0.663 | C1 |
| 9 | How do false positive rate and the guardrail stack interact in the pro | multi_context | 0.73 | 0.742 | 0.59 | 0.65 | 0.678 | C1 |
| 10 | How do hybrid search and the guardrail stack interact in the productio | multi_context | 0.775 | 0.706 | 0.65 | 0.625 | 0.689 | C1 |

## Clusters Identified

### Cluster C1: Multi-hop and cross-context failures

**Pattern:** Multi-context questions need facts from more than one chunk, but the offline baseline only uses two static contexts.

**Examples:**
- How do Llama Guard and the guardrail stack interact in the production blueprint?
- How do SLO thresholds and the guardrail stack interact in the production blueprint?

**Root cause:** Retriever configuration is too shallow for cross-document synthesis.

**Proposed fix:** Increase `top_k` from 3 to 6, add a cross-encoder reranker, and keep a hybrid BM25 + vector fallback for exact terms.

### Cluster C2: Retrieval precision drops

**Pattern:** Some answers include generic Lab 24 context but miss the exact metric requested.

**Examples:**
- Why should multi-hop retrieval be monitored together with guardrail latency?
- Why should hybrid search be monitored together with guardrail latency?

**Root cause:** The retriever overweights broad terms like `lab`, `evaluation`, and `guardrail`.

**Proposed fix:** Add metadata filters by phase, use chunk titles in embeddings, and tune MMR diversity to reduce duplicated context.

### Cluster C3: Safety-policy ambiguity

**Pattern:** Questions involving guardrail refusal and output safety sometimes need policy context not present in retrieved chunks.

**Examples:**
- What does false positive rate measure in Lab 24?
- What does refuse rate measure in Lab 24?

**Root cause:** Safety taxonomy and refusal policy are not indexed as first-class documents.

**Proposed fix:** Add a dedicated policy corpus with category labels, then evaluate policy retrieval separately from general RAG retrieval.
