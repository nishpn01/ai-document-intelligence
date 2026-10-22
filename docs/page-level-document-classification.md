# Page-level document classification — Mistral vs Gemini on boundary detection

Notebook: [`16-page-level-detection-strategy.ipynb`](../notebooks/16-page-level-detection-strategy.ipynb)
Source report retained privately; this summary records the historical findings and scope.

## The question

Can a local, quantized open-source model reliably classify document pages by type, especially
at document boundaries? How does it compare to a hosted model?

## The answer

**Mistral-7B replaced an earlier Gemini version because the pipeline makes one model call per
page, and that exhausted the free-tier daily quota on a 10-page file.** A local model removes
that ceiling — no API key, no per-request cap.

**Mistral-7B-Instruct got 9 of 10 pages right.** It correctly split two back-to-back
Certificates of Quality (different products) into separate documents and classified all other
pages accurately.

The one miss was a Material Description Sheet that opened with a new title and identifier. The model marked it as a continuation of the previous BSE/TSE Declaration. Gemini had
classified it correctly — this was a genuine boundary-reasoning weakness of the smaller model.

The setup used grammar-constrained decoding (JSON schema enforcement) to ensure every response
was structurally valid JSON. The model could not return malformed output, but schema validity
does not guarantee semantic correctness.

## Historical results

| Measure | Value |
| --- | --- |
| Total pages in test file | 10 |
| Pages correctly classified by Mistral | 9 |
| Pages misclassified | 1 (page 6: Material Description Sheet marked as continuation of BSE/TSE) |
| Back-to-back Certificate splits | Correctly identified both as separate documents |
| Gemini (comparison) | Split page 6 correctly |
| Grammar-constrained output | All responses valid JSON; no malformed output |

## Test conditions

One 10-page file with mixed document types (Certificates of Quality, Material Description
Sheets, BSE/TSE Declarations, and other content). The model made one classification decision
per page. Mistral-7B-Instruct v0.2, 4-bit quantized (GGUF), running locally via
llama-cpp-python. **One file, 10 pages.** The test does not cover other document types or
multiple files.

## What else it found

- **Boundary reasoning was a weakness in this small test.** One page with a new title and identifier was treated as a continuation; Gemini classified it correctly.
- **Grammar-constrained decoding prevents malformed output but doesn't fix semantic
  reasoning.** The JSON was always valid, but that didn't prevent the misclassification.
- **Few-shot examples and header comparison may help.** Add examples of document boundaries and compare page headers directly.
