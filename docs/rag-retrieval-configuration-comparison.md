# RAG retrieval configuration comparison — filter and re-rank trade-offs

Notebook: [`11-embedding-comparison-with-reranking.ipynb`](../notebooks/11-embedding-comparison-with-reranking.ipynb)
Source report retained privately; this summary records the historical findings and scope.

## The question

On a small, uniform document, does filtering by similarity threshold or re-ranking results
improve answer completeness, or does extra configuration hurt by pruning relevant context?

## The answer

**Configuration A (no threshold, no reranker) was the best.** It returned the complete list of
all four QC test methods. Adding a similarity threshold or cross-encoder reranking did not
improve the answer and, in one case, made it worse.

Configuration B produced an identical answer to A — the threshold had no filtering effect.
**Configuration C, the most advanced setup, was the worst.** Adding a cross-encoder reranker
narrowed the five retrieved chunks to three and dropped three of the four QC tests from the
final answer, keeping only the compliance details.

The takeaway: on a small, uniformly relevant document, simpler is better. Extra filtering and
re-ranking can prune useful context without gaining anything in return.

## Results

| Configuration | Top_k | Similarity threshold | Reranker | Chunks retrieved | Answer completeness | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| A (baseline) | 5 | None | No | 5 | All 4 QC tests (Pressure Hold, Visual Inspection, Package Integrity, USP <88> bio-safety) | 4/5 |
| B (threshold) | 8 | 0.25 | No | 5 | Same as A — all 4 tests | 4/5 |
| C (reranker) | 5 | 0.25 | Yes (cross-encoder) | 3 (after rerank) | Only USP bio-safety + ISO 9001 compliance — dropped the three physical tests | 3/5 |

## Test conditions

One SDF document, one query (a question about quality-control methods), retrieved
against three different retriever configurations. **One document, one query.** The three
configurations tested top_k values of 5 to 8, similarity thresholds from none to 0.25, and
with/without cross-encoder re-ranking.

## What else it found

- **Threshold filtering did nothing on this document.** All retrieved chunks scored above the
  0.25 threshold, so the filter left the results untouched.
- **The reranker narrowed too aggressively.** Reducing 5 chunks to 3 eliminated useful context.
  The confidence score dropped from 4 to 3, and the final answer lost detail.
- **Smaller document sets may not benefit from ranking.** On a 3-page SDF where all chunks are
  relevant, re-sorting adds overhead without gain — the most advanced configuration in the
  comparison was the one that performed worst.
