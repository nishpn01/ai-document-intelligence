# Full RAG chatbot capstone — design and trade-offs

Public adaptation: [`19-full-rag-chatbot-capstone.ipynb`](../notebooks/19-full-rag-chatbot-capstone.ipynb). The original input and saved run outputs remain private.
Source report retained privately; this summary records the historical findings and scope.

## The question

In a modular Gradio-based RAG chatbot with inference in the notebook runtime, what matters most for answer quality:
retrieval quality, prompt engineering, metadata tracking, or filtering? Where do errors come
from when they do occur?

## The answer

**Prompting mattered most.** The quality of the prompt instruction — telling the model to use
only the provided context and cite sources — was the most direct lever on answer accuracy.
Retrieval reliably pulled the correct pages, but whether the model then answered cleanly and
grounded depended on the prompt.

Metadata mattered as the backbone for traceability, showing which page each answer came from.
Filtering had limited effect on this document.

Errors came from generation, not retrieval: multi-part questions caused the model to cut
answers short (token limit too low) or generate its own follow-up questions instead of
stopping.

## Pipeline

All seven required components were present: OCR-fallback document processing, metadata
tagging (`doc_type`, `page_start`/`page_end`, `chunk_index`, `source_file`), BGE-small
embeddings into a LlamaIndex `VectorStoreIndex`, context-grounded prompting with forced
citation, Mistral-7B via llama-cpp (explicitly not Gemini), top-4 retrieval returning answer +
sources + confidence + chunk count, and a two-column Gradio UI.

**Historical run:** 10 pages, 28 chunks, with cited answers and 4 retrieved chunks per query. The original input and answer text are retained privately. Reported confidence values measure retrieval similarity, not answer correctness.

## Historical results

| Component | Finding |
| --- | --- |
| Retrieval accuracy | Reliably found correct source pages (e.g., page 5 for BSE/TSE dates) |
| Prompt instruction | A context-only instruction helped keep answers grounded |
| Metadata (page-level sources) | Enabled answer traceability but did not directly improve answer quality |
| Filtering | Did not help on this sample |
| Generation errors | Multi-part questions: answers cut off mid-sentence; model generated follow-ups unprompted |
| Inference speed | ~229 seconds per query on local Mistral-7B; would be a bottleneck at scale |

## Three honest defects, documented

- One query took ~229 seconds. A local 7B model on a free GPU is too slow for interactive use.
- A multi-part answer was truncated mid-sentence — `max_new_tokens` set too low.
- One answer over-generated an unasked Q&A, the model continuing the prompt pattern.

## Confidence score

Mean similarity across retrieved chunks. It measures *retrieval* relevance, not answer correctness.

## Test conditions

One PDF document, evaluated with multiple Q&A pairs. The chatbot used PyPDF2 + Tesseract OCR
for extraction, RecursiveCharacterTextSplitter chunking (512 chars, 100 overlap),
BAAI/bge-small-en-v1.5 embeddings, LlamaIndex vector storage, top-4 retrieval, and Mistral-7B run in the notebook runtime for generation. **One document.** The scope does not cover multi-document scenarios
or large corpora.

## What else it found

- **Token limit and prompt discipline are separate problems.** The report discusses raising the output limit and adding a stop sequence. The checked notebook still sets `max_new_tokens=256` without an explicit stop sequence, so this public edition does not claim the defects are fixed.
- **Scaling to a large corpus would require architecture changes.** Don't rebuild the index on every
  upload; use a persistent vector DB (FAISS, Chroma, Pinecone), filter by metadata before
  semantic search, and consider faster embedding or inference.
- **Design finding:** swapping the mocked `handle_chat` / `process_pdf` for the real RAG
  functions required zero UI changes. Separation of concerns held.
- **Environment friction, not design friction:** the UI task was mostly Gradio 6.0 breaking
  changes — `gr.Chatbot` messages-only format, the `type` argument removed, `theme` relocated
  from `gr.Blocks()` to `.launch()`.

This is the same pipeline the [final pipeline evaluation](final-pipeline-evaluation.md) later
scored formally — this report is where the truncation and over-generation defects were first
observed, and where the latency problem first showed up (~229 s on this run; ~292 s/query
average in the later formal evaluation).
