# Embedding model comparison — MiniLM vs E5 vs BGE

Notebooks: [`10-embedding-model-comparison.ipynb`](../notebooks/10-embedding-model-comparison.ipynb),
[`11-embedding-comparison-with-reranking.ipynb`](../notebooks/11-embedding-comparison-with-reranking.ipynb)
Source report retained privately; this summary records the historical findings and scope.

## The question

Which open-source embedding model retrieves the most useful chunks from a pharmaceutical SDF,
and at what speed?

## The answer

**MiniLM (`sentence-transformers/all-MiniLM-L6-v2`), scored 5 of 5.** All three models
retrieved relevant context on all three queries, so retrieval quality did not separate them.
MiniLM won on speed and consistency — fastest on every query, roughly 1.5× to 2× faster than
E5 and BGE, and the smallest model to run.

**But no single model won every query**, and that is the more useful finding. E5 was the
slowest model overall yet pulled the sharpest chunk on the hardest query — it retrieved the
the most specific test-method table where
the faster models returned more general context. The best model depended on the question type.

## Results

| Criterion | MiniLM | E5 | BGE |
| --- | --- | --- | --- |
| Model | `sentence-transformers/all-MiniLM-L6-v2` | `intfloat/e5-small-v2` | `BAAI/bge-small-en-v1.5` |
| Answer quality | Retrieval only; relevant blocks | Retrieval only; relevant blocks | Retrieval only; relevant blocks |
| Context relevance | Right block on all 3 | Strongest on the QC-methods query | Best chunk on storage; right block on all 3 |
| Speed (3 rounds, seconds) | 1.94, 2.05, 2.99 — fastest all 3 | 3.24, 4.02, 4.61 — slowest 2 of 3 | 4.64, 3.34, 3.35 — middle |
| Consistency | Relevant every query, fastest every time | Relevant on all 3, strongest on hardest | Relevant on all 3 |
| **Overall (1–5)** | **5** | **4** | **4** |

## Test conditions

One sample SDF document and three queries. The date is omitted. **The LLM was disabled
(`Settings.llm = None`), so there was no generated answer** — the comparison judged retrieved
chunks directly, not answer quality. Three rounds per model for timing.

Scale is small: one document, three queries. The report says so itself — On this small document, all three models retrieved relevant material; retrieval quality did not decide the ranking.

## What else it found

- **Judging chunks instead of answers changed the evaluation.** With the LLM off, the reading
  was of what each model actually pulled rather than how it phrased a response. The report
  names this as a benefit — it forced closer attention to retrieval itself.
- **First-run timings are not real timings.** The initial run was slow because the models had
  to download; true speed only appeared on later runs.
- **The speed-vs-accuracy trade-off is the headline tension.** The slowest model gave the most
  precise answer on the hardest question.

### Model used in the final evaluation

**This comparison scored MiniLM best, but the capstone and final evaluation notebooks
(the capstone chatbot and the final evaluation) uses `BAAI/bge-small-en-v1.5`.** The reason
wasn't recorded at the time. See the [final pipeline evaluation](final-pipeline-evaluation.md)
for where BGE is actually used.
