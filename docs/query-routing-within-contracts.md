# Query routing within contracts — chunking, metadata, and precision limits

Notebook: [`15-route-queries-within-contract.ipynb`](../notebooks/15-route-queries-within-contract.ipynb)
Source report retained privately; this summary records the historical findings and scope.

## The question

For a large multi-page contract, does sliding-window chunking or page-level splits work
better? Does metadata filtering actually reduce noise? And can RAG be trusted to extract
exact terms from legal documents?

## The answer

**Sliding-window chunking with overlap preserved continuity better than page splits.** A
100-character overlap kept related content (a Configuration Change History table and its
linked Drawing Changes) together across chunk boundaries, avoiding fragmentation.

**Metadata filtering only worked when labels were truly distinct.** Generic "Packaging
Specification" labels on all relevant pages didn't exclude off-topic content. The metadata
filter passed through all four retrieved chunks (three on-topic, one irrelevant
Chain-of-Custody section). The model ignored the noise and answered correctly, but the filter
didn't do the work.

**RAG is not reliable for exact term extraction in legal documents.** Retrieval located the relevant material change and effective date, but generation altered a reference identifier. The recommendation is to use retrieval to locate sections, then verify exact terms manually.

## Results

| Aspect | Finding |
| --- | --- |
| Sliding-window chunking (100-char overlap) | Kept related content together across chunk boundaries; finer granularity than page-level |
| Page-level chunking | Would split dense tables and lose continuity when content spanned pages |
| Metadata filter effect | Did not narrow results; all pages shared the same generic section label |
| Retrieved chunks: on-topic | 3 of 4 (correct packaging pages) |
| Retrieved chunks: off-topic | 1 of 4 (Chain-of-Custody, irrelevant) |
| Answer accuracy (substance) | Correctly located the described material change and its effective date |
| Answer accuracy (identifiers) | Incorrect: the generated reference identifier did not match the source |

## Test conditions

One multi-page contract PDF. Retrieved 4 chunks for one query. **One document, one query.**
The test does not cover multiple documents, multiple queries, or other contract types.

## What else it found

- **Semantic similarity did the real work, not filtering.** The model synthesizer ignored the
  irrelevant chunk (Chain-of-Custody) and produced the right answer, but only because semantic
  relevance was high for the on-topic chunks. The metadata filter never narrowed the set.
- **Precision labels matter more than broad categories.** To make metadata filtering work,
  label by section type (specification, certificate, or chain-of-custody) so the
  filter can exclude out-of-scope pages.
- **Generative answers can hallucinate reference numbers even when retrieval is correct.** The
  source material had a reference identifier; the model changed it. For legal contracts, extractive
  (copy exact text) answers, or a lower generation temperature, would be the safer choice.
