# RAG pipeline design — architecture and verification

Source report retained privately; this summary records the historical findings and scope.

## The question

Given a modular pipeline design with local embeddings, page-level chunking, hybrid retrieval,
and inference in the notebook runtime, does it answer questions about pharmaceutical documents?

## The answer

The pipeline returned grounded answers for two test queries on one SDF document. The finding is limited to those queries.

One query about quality-control methods returned a list of test methods. The source-specific answer is omitted.

A second query correctly noted that
the certificate does not specify storage conditions, but returned the recommended temperature
for the product’s recommended storage condition.

## Test conditions

Two queries, one 3-page SDF Certificate of Quality. The pipeline used all-MiniLM-L6-v2
embedding (local, no API key), page-level chunking with PyMuPDF (one chunk per page for 3
pages), and hybrid retrieval (vector + BM25) with cross-encoder reranking. The report does not
state which model generated the two responses. **Two queries on one document.** The scope is
narrow and does not establish general reliability.

## What else it found

- **A local, no-API-key embedding model keeps the pipeline free and private.** Stated reason
  for choosing all-MiniLM-L6-v2: nothing gets sent to a paid cloud embedding service.
- **Page-level chunking preserves section structure.** Each page stays intact, keeping field
  labels tied to values.
- **Hybrid retrieval caught both exact matches and semantic similarity.** BM25 catches exact
  terms like a test name or a document identifier; vector search finds the right content even when the
  question is worded differently from the document.
