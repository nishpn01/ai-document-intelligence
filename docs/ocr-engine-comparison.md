# OCR engine comparison — Tesseract vs PaddleOCR vs EasyOCR

Notebook: [`06-layout-ocr-engine-comparison.ipynb`](../notebooks/06-layout-ocr-engine-comparison.ipynb)
Source report retained privately; this summary records the historical findings and scope.

## The question

Which OCR engine reads a scanned pharmaceutical certificate most reliably, and which is
best suited to a compliance workflow where a field's value has to stay attached to its label?

## The answer

**PaddleOCR, for this document.** It had the highest average engine-reported confidence (98.41%), no low-confidence reads, and was the only engine that kept a sampled label attached to its value.

**Tesseract was a close second and read the most complete text** — 220 words against
PaddleOCR's 36 regions — so the recommendation is not a clean single winner. The report recommends combining them: Tesseract for dense body text, PaddleOCR for structured fields
and tables. EasyOCR is left out for this document type.

All three engines read the sampled core fields. The comparison found differences in reported confidence, grouping, and layout handling; it did not establish general extraction accuracy.

## Historical results

| Measure | Tesseract | PaddleOCR | EasyOCR |
| --- | --- | --- | --- |
| Sampled fields captured | All correct | All correct | All correct, lower reported confidence |
| Average confidence | 93.90% | 98.41% | 79.12% |
| Text regions / words detected | 220 | 36 | 47 |
| High-confidence reads (>90%) | 209 of 220 | 36 of 36 | 17 of 47 |
| Low-confidence reads (<50%) | 2 | 0 | 3 |
| Groups label with its value | No | Yes | No — splits them |
| Reads the table row | Yes | Partial | Fragmented |
| Handled product name | Yes | Yes | Recognition was imperfect |
| Setup | Easy, first try | Hard — needed downgrade and restart | Easy, first try |

Every one of nine key pharmaceutical terms (certificate, lot, expiration, date, manufacture,
article, quality, product, vendor) was found by all three engines. `BATCH` was found by none.

**A caveat on comparing the confidence columns.** The engines report in different units —
Tesseract counts 220 *words*, PaddleOCR 36 *regions*, EasyOCR 47 *regions*. "209 of 220"
and "36 of 36" are therefore not measuring the same thing, and the high-confidence row should
be read within an engine rather than across them.

## Test conditions

One scanned certificate page was run through all three engines. **A single document and a single page.** The conclusions are
scoped to a clean, well-structured certificate; nothing here tests a degraded scan, an
unusual layout, or a multi-page document. Environment was Google Colab on CPU.

## What else it found

- **The layout-aware engines did not clearly beat plain Tesseract.** The expectation going in
  was that PaddleOCR and EasyOCR would win comfortably on a structured document. On a clean
  certificate, Tesseract held its own.
- **EasyOCR needed more cleanup in this sample.** Its reported confidence was lowest here — 79% average confidence, only 17 of 47 regions above 90%, and it
  had imperfect product-name recognition. Nothing degenerated into gibberish, but its output needs the most cleanup.
- **Field splitting is the compliance-relevant failure.** EasyOCR separated
  a field label from its value. In a compliance record that is the error class
  that puts the wrong value in the wrong field — a worse outcome than a low-confidence read,
  because it is silent.
- **PaddleOCR's setup was the real cost.** The current version would not run on Colab's CPU
  and raised `NotImplementedError`; it required pinning back to `paddlepaddle 2.6.2` and a
  runtime restart. Tesseract and EasyOCR both installed and ran first try. The engine with the highest reported confidence was the most expensive to set up.
- **Tesseract surfaced a vendor attribution** that the other engines did not show in the sampled output.
