# PyMuPDF SDF extraction — text and structure recovery

Notebook: [`04-extract-text-multipage-pdf.ipynb`](../notebooks/04-extract-text-multipage-pdf.ipynb)
Source report retained privately; this summary records the historical findings and scope.

## The question

Can PyMuPDF extract all text and structural information from an SDF, and what are the limits
of word-level extraction for structured data?

## The answer

**Text extraction worked well; structure extraction requires additional work.** PyMuPDF's
`get_text("words")` pulled all 617 words from a 3-page SDF and returned each with its bounding
box. Body text and certificate text came out clean and readable. Every word was localized to
its exact position on the page.

Tables were the weak point. Table headers came out as separate entries in reading order rather than as a cohesive
row. Rebuilding row-and-column structure requires using the bounding-box coordinates to
reconstruct the layout — doable, but not automatic.

Multi-word field values split into separate entries during extraction.
Stitching them back into one field value needs coordinate-based grouping.

## Results

| Measure | Value |
| --- | --- |
| Total words extracted | 617 |
| Words with bounding boxes | All 617 |
| Body text quality | Clean and readable |
| Certificate text quality | Clean, complete |
| Special characters | Preserved correctly |
| Table structure preserved | No — cells read in order, not as rows |
| Multi-word field grouping | Splits into separate words |

## Test conditions

One three-page SDF document. Extraction used PyMuPDF's `get_text("words")` method and saved
output to JSON. **One document.** The sample does not test degraded scans, unusual layouts, or
other document types.

## What else it found

- **Bounding boxes enable reconstruction but add complexity.** Coordinates let you rebuild
  layout, but you have to write logic to group words by position.
- **Special characters survived extraction** in the tested document.
- **Reading order does not equal layout.** Naively stitching words in order will mangle tables
  and lose field grouping.
