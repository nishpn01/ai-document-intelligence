# Final pipeline evaluation

Historical results below refer to the original private input. A [public-fixture adaptation of notebook 20](../notebooks/20-pipeline-evaluation.ipynb) is included separately; it does not contain or reproduce the original answer key.

A dedicated evaluation notebook, separate from the capstone chatbot, reproducing the full
pipeline end to end and scoring it against a hand-verified answer key.

## Pipeline under test

PyPDF2 page extraction with Tesseract OCR fallback → `RecursiveCharacterTextSplitter`
(chunk 512, overlap 100) → `BAAI/bge-small-en-v1.5` embeddings → LlamaIndex in-memory index →
`similarity_top_k=4` → Mistral-7B-Instruct v0.2 (Q4_K_M GGUF, llama-cpp).

## Corpus and ground truth

**10 pages, 28 chunks** in the historical input. Five question-and-answer pairs were checked by hand against that source. This public edition does not include the original input or answer key.

**Every number below is scoped to this test set — five questions over ten pages and
twenty-eight chunks. It is not a claim about the pipeline's general extraction accuracy.**

## Final metrics (5-question test set, 10 pages, 28 chunks)

| Metric | Result |
| --- | --- |
| Exact Match | 100% |
| Retrieval Recall@4 | 100% |
| MRR | 0.87 |
| Precision@4 | 45% |
| Hit Rate | 100% |
| Avg latency | 292 s / query |
| Retrieval time | 88 ms |

## The best story in the project: bad ground truth, not a bad pipeline

The first evaluation run scored **80% Exact Match / 60% Recall**. Both apparent misses traced to errors in the hand-built ground truth: a wrong page label and an ambiguous identifier question. After checking the answer key against the source, the same pipeline scored **100% / 100%**.

Bad ground truth produces misleading metrics. The fix wasn't in the retrieval or the model —
it was in the test itself, and only caught by checking the failures against the source
document rather than trusting the score.

## The wrong-document retrieval

The historical input contained two Certificates of Quality for different products. A generic identifier question retrieved a correct value from the wrong certificate.

A document-type filter alone cannot distinguish two certificates of the same type. The next change is to select the intended certificate with a stable document identifier or page range, or ask the user which certificate they mean. This is a recommendation; it is not implemented.

## The Precision@4 tension, named honestly

Recall@4 is 100% while Precision@4 is 45%. Retrieval finds the right passage every time, but
brings roughly half irrelevant context along with it. **Not addressed in the current build.**
On a 28-chunk corpus this doesn't cost much; at scale it means the model is reading twice as
much irrelevant context as relevant context on every query.

## Latency

**~292 seconds per query on average.** This is Mistral-7B-Instruct (Q4_K_M GGUF) running
locally via llama-cpp. Not viable for an interactive chat experience at this speed — see
[Limitations](../README.md#limitations) in the README for what this means for the pipeline as
a whole.
