# AI Document Intelligence

This is the public-facing edition of a document-AI project developed during my Pfizer externship with Extern. I ran OCR and embedding comparisons, evaluated document question answering against a manually checked answer key, and documented the failures and tradeoffs, with AI assistance for code and documentation.

The project used guided learning resources and starter material. This edition preserves the analysis and sanitized notebook code, excludes the original supplied documents and report/deck files, and adds fictional sample documents for a public demonstration. It is a learning and evaluation project, not a production Pfizer system or a statement of employment at Pfizer.

**Start here:** [Evaluation findings](docs/final-pipeline-evaluation.md), [OCR comparison](docs/ocr-engine-comparison.md), and [public demo instructions](#running-it).

## Project and release dates

- Original learning and project work: June through August 2026, with project work continuing through August 31, as recorded in the original project documentation.
- Original repository history: initial commit July 29; notebook and report import August 20; evaluation and documentation updates September 1–2, 2026.
- This separate public edition: October 21, 2026. Its commits record preparation and publication of this edition. They are not presented as the original experiment dates, and the private source history is not copied into this repository.

## Contents

- [What this found](#what-this-found)
- [How it works](#how-it-works)
- [Studies](#studies)
- [Repository guide](#repository-guide)
  - [Data sources](#data-sources)
- [Limitations](#limitations)
- [What's next](#whats-next)
- [Running it](#running-it)
- [Stack](#stack)

## What this found

**Final pipeline evaluation - 5 questions, 10 pages, 28 chunks:**

| Metric | Result |
| --- | --- |
| Exact Match | 100% (5-question test set) |
| Retrieval Recall@4 | 100% (same 5-question, 28-chunk test set) |
| MRR | 0.87 |
| Precision@4 | 45% |
| Avg latency | ~292 s / query |
| Retrieval time | 88 ms |

Full writeup, including the answer-key correction and the retrieval failure below:
[`docs/final-pipeline-evaluation.md`](docs/final-pipeline-evaluation.md).

**Evaluation: the first run measured the test set, not the model.** The first
evaluation run scored 80% Exact Match / 60% Recall. Both apparent misses traced to errors in
the hand-built ground truth, not the pipeline - a wrong page label and an ambiguous
lot-number question. After correcting the answer key against the source PDF, the same
pipeline scored 100% / 100% on that same 5-question set. Bad ground truth produces misleading
metrics, and the fix was in the test, not the model.

**A correct answer from the wrong document.** The evaluation PDF contains two certificates of the same type. A generic question about a lot number returned a real value from the wrong certificate. A document-type filter alone cannot distinguish two certificates of the same type. A proposed next change is to select a specific document or page range, or ask which certificate the user means. This is not claimed as an implemented fix.

**OCR showed a grouping-versus-coverage tradeoff on one page.**
The report records engine-reported average confidence of 98.41% for PaddleOCR and 93.90% for Tesseract. These are not comparable accuracy scores. Tesseract returned 220 words and PaddleOCR 36 regions, which are different output units. All three tested engines captured the core fields; grouping, table handling, text coverage, and setup effort were the more useful distinctions. The report recommends combining them: Tesseract for
dense body text, PaddleOCR for structured fields and tables. See
[`docs/ocr-engine-comparison.md`](docs/ocr-engine-comparison.md).

**The most advanced retrieval configuration was the worst one.** Comparing three retrieval
setups on the same query, enabling a cross-encoder reranker narrowed five retrieved chunks to
three and dropped three of the four QC test methods from the final answer. The plain,
unfiltered baseline configuration gave the complete answer. See
[`docs/rag-retrieval-configuration-comparison.md`](docs/rag-retrieval-configuration-comparison.md).

## How it works

- **OCR fallback, not OCR-only.** Pages are read from the PDF's digital text layer first; a
  near-empty page is treated as scanned and sent through OCR instead. Pharmaceutical
  documents mix both kinds of page in a single file, so a single strategy doesn't cover the
  corpus.
- **Bilateral filter + adaptive threshold before OCR**, not raw scans. Preprocessing improved
  what OCR had to work with.
- **Detailed classification-prompt engineering**, because a vaguer prompt classified every
  document as "Other." Naming the document types explicitly fixed the failure mode.
- **Metadata-filtered retrieval** (`doc_type`, `page_start`/`page_end`, `source_file`) was
  explored as a way to narrow retrieval. Two certificates of the same type still require a stable document identifier, page range, or clarification.
- **Prompt guardrails that force citation and allow abstention on weak context**, after
  observing that answer quality depended more on prompt discipline than on retrieval or
  metadata.
- **Hosted Gemini compared with Mistral-7B in the notebook runtime.** Gemini was faster and hit its
  free-tier rate limit repeatedly (429 errors); Mistral was slower and ran inference in the notebook runtime rather than sending prompts to the hosted Gemini API. Google Colab is still a cloud-hosted environment; this is not a wholly on-device or compliance claim. See
  [`docs/gemini-vs-mistral.md`](docs/gemini-vs-mistral.md) for the comparison that backs this
  choice, and the [final evaluation](docs/final-pipeline-evaluation.md) for what the slower
  model costs in practice (~292 s/query).

**The final evaluation uses a different embedding model from the comparison's top-rated model.** The written
comparison scored MiniLM best on every measured criterion, but the capstone and final evaluation notebooks uses `BAAI/bge-small-en-v1.5`. The reason wasn't recorded
at the time. See [`docs/embedding-model-comparison.md`](docs/embedding-model-comparison.md).

## Studies

The readable studies in `docs/` summarize the original experiments. Supplied PDFs and report/deck files are not included in this public edition. Notebook links identify the relevant historical experiment or its sanitized public adaptation. Historical results are not outputs from the new fictional sample documents.

| Study | What it found |
| --- | --- |
| [Final pipeline evaluation](docs/final-pipeline-evaluation.md) | 100% Exact Match / 100% Recall@4 on 5 questions; the answer-key story; wrong-document retrieval |
| [OCR engine comparison](docs/ocr-engine-comparison.md) | PaddleOCR most confident, Tesseract most complete; recommendation is to combine them |
| [Embedding model comparison](docs/embedding-model-comparison.md) | MiniLM fastest and most consistent; no single model won every query |
| [Gemini vs Mistral](docs/gemini-vs-mistral.md) | Both stayed grounded; the gap was speed, not accuracy |
| [RAG retrieval configuration comparison](docs/rag-retrieval-configuration-comparison.md) | Simpler retrieval beat the reranked configuration |
| [RAG pipeline design](docs/rag-pipeline-design.md) | Early architecture verification - hybrid retrieval, page-level chunking |
| [Full RAG chatbot capstone](docs/rag-chatbot-capstone.md) | The working Gradio app; three documented defects (latency, truncation, over-generation) |
| [PDF structure extraction](docs/pdf-structure-extraction.md) | PyMuPDF word-level extraction works; table structure does not survive automatically |
| [Query routing within contracts](docs/query-routing-within-contracts.md) | RAG located the right section but garbled a generated identifier |
| [Page-level document classification](docs/page-level-document-classification.md) | Local Mistral-7B split document boundaries correctly on 9 of 10 pages |

## Repository guide

| Path | Contents |
| --- | --- |
| `docs/` | Experiment findings, data provenance, and public-demo verification |
| `notebooks/` | Numbered experiments; 19 and 20 are adapted for public sample inputs |
| `data/public-fixtures/` | Fictional PDF inputs, checked answer key, and offline check records |
| `scripts/` | Fixture generation and a lightweight offline reference demonstration |
| `tests/` | Checks for the permitted public fixture and reference behavior |

### Data sources

The original learning project used supplied pharmaceutical documents. Those inputs, original PDF reports, presentations, extracted source text, and their Git history are not distributed here. The public fixture contains clearly fictional examples. See [data provenance](docs/data-sources.md) for the boundary between historical results and the public demonstration.

Earlier notebooks are historical experiments and may reference unavailable original inputs. Their saved outputs have been removed where necessary. Their presence is not a claim that all twenty notebooks run unchanged against the new fixture.

Notebook 07 is omitted because its source embeds document-specific extracted values. Its original remains private.

### Notebooks in sequence

| # | Notebook | Stage |
| --- | --- | --- |
| 01–03 | text/tabular/image cleaning | Cleaning |
| 04–06 | multi-page PDF extraction, scanned-PDF analysis and OCR engine comparison | Extraction & OCR |
| 08–11 | chunking, simple Gemini chatbot, embedding comparisons (with and without reranking) | Embeddings & chunking |
| 12–13 | advanced PDF retrieval, open-source model retrieval | Retrieval |
| 14–16 | routing across PDFs, routing within a contract, page-level boundary detection | Routing |
| 17–19 | Gradio basics, a document Q&A UI, the full RAG chatbot capstone | Application |
| 20 | final pipeline evaluation | Evaluation |

## Limitations

- **~292 s/query is not viable for interactive use.** That's the average latency of the local
  Mistral-7B-Instruct model (Q4_K_M GGUF) on a free-tier GPU. A synchronous chat interface at
  this speed does not work; the capstone chatbot observed a single query take ~229 seconds in
  an earlier run.
- **Retrieval recall and retrieval precision disagree.** Recall@4 is 100% on the 5-question
  evaluation set, but Precision@4 is 45% - retrieval finds the right passage every time, but
  brings roughly half irrelevant context along with it. Not addressed in the current build.
- **Every test set here is small.** The formal evaluation is 5 questions
  over one PDF containing multiple document types, with 10 pages and 28 chunks. The OCR, embedding, retrieval-configuration, and
  Gemini-vs-Mistral comparisons are each one document and one to three queries. None of this
  has been run against a larger or more varied corpus.
- **Answer generation truncates and over-generates.** A multi-part question was cut off
  mid-sentence because `max_new_tokens` was set too low; a separate answer continued past the
  question into an unasked, self-generated follow-up Q&A.
- **Page-level document-boundary classification missed 1 of 10 pages** in the one file it was
  tested on - a smaller-model boundary-reasoning weakness that a hosted model (Gemini) did not
  share on that same page.
- **RAG can garble a generated identifier even when retrieval is correct.** On a contract-PDF
  routing test, the retrieved section was right but the model wrote the wrong ECN number.
  Extractive answers, not generated ones, are the safer choice for exact reference numbers.

## What's next

- Re-run the embedding comparison against the final pipeline's own documents and chunking
  strategy, to establish which model - MiniLM or BGE - is actually better for this corpus.
- Disambiguate the intended document or page range before answering a generic lot-number question. A `doc_type` filter alone does not separate two certificates of the same type.
- Address the Precision@4 gap - the retrieval configuration comparison found that the current
  fixes (thresholding, reranking) don't do it, so a different approach is needed.
- Move off synchronous local inference, or add a persistent vector index, before testing
  against a corpus larger than a handful of documents.

## Running it

Use the fictional input and the lightweight offline check first. It is a reference demonstration of extraction, source selection, and extractive answering, not a rerun of the historical embedding/Mistral evaluation.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-demo.txt
```

The exact fixture-generation and check commands are listed in [the fixture guide](data/public-fixtures/README.md) and [the public run record](docs/public-fixture-run.md). The offline demonstration makes no hosted AI calls.

For the original model-based workflow, open [notebook 19](notebooks/19-full-rag-chatbot-capstone.ipynb), followed by [notebook 20](notebooks/20-pipeline-evaluation.ipynb), using their public-fixture setup cells. They require their documented model/runtime dependencies and may require a GPU. The large-model notebooks have not been re-executed for this public release unless the run record explicitly says otherwise. Historical results remain labeled as historical.

Earlier Gemini experiments read credentials from Colab Secrets. No credentials are included. Supply only documents you are permitted to process.

## Stack

- **Retrieval** - LlamaIndex in-memory vector index; BM25/hybrid retrieval in the comparison experiments
- **LLMs** - Mistral-7B-Instruct v0.2 (Q4_K_M GGUF, via `llama-cpp-python`) in the capstone and final evaluation; Gemini in the earlier notebooks
- **Embeddings** - `BAAI/bge-small-en-v1.5` in the capstone and final evaluation;
  `sentence-transformers/all-MiniLM-L6-v2` and `intfloat/e5-small-v2` in the comparison work
- **OCR** - Tesseract, PaddleOCR, EasyOCR
- **PDF** - PyMuPDF (`fitz`), PyPDF2, `pdf2image` + poppler
- **UI** - Gradio
