# Hosted Gemini vs Mistral-7B in a notebook runtime

Notebook: [`13-rag-with-open-source-models.ipynb`](../notebooks/13-rag-with-open-source-models.ipynb)
Source report retained privately; this summary records the historical findings and scope.

## The question

Is an open-source model run in the notebook runtime good enough to answer questions about pharmaceutical
documents, or does a hosted cloud model win outright?

## The answer

**Both stayed grounded and neither hallucinated. The gap was speed, not quality — and on one
query the slower local model was better.**

Gemini was faster by a wide margin (near-instant vs 60–110 seconds per answer) and returned
tidier, better-structured output. But on the storage-conditions query, **Mistral pulled more
detail than Gemini** — it surfaced the +2–40 °C operating range and acclimation advice that
Gemini omitted. The conclusion drawn: *slower did not mean worse; the main measured cost of the
open-source route was speed.*

For pharmaceutical documents the recommendation leans open-source, on two grounds that have
nothing to do with answer quality: **Gemini's free tier hit rate limits repeatedly (429
errors)**, which would not survive volume, and Mistral inference ran in the notebook runtime rather than through the hosted Gemini API. This comparison does not establish an on-device or compliance guarantee.

## Results

| Dimension | Gemini | Mistral-7B | Verdict |
| --- | --- | --- | --- |
| Sterilization method | Autoclave for pump tubing (121 °C >15 min); gamma irradiation for inlets (25–40 kGy) | Same, phrased as prose | Both correct, essentially matched |
| QC test methods | Clean list of all 6 | Flow rate, pressure integrity, visual inspection, USP <88> Class VI; hedged on autoclave/gamma | Gemini cleaner and more complete |
| Storage conditions | Provided a narrower answer | Mistral included more surrounding detail |
| Speed | Near-instant, but hit free-tier rate limits (429) repeatedly | ~1.4–1.5 tokens/sec; ~60–110 sec per answer on a free T4 | Clear speed win for Gemini |
| Accuracy / grounding | Grounded, correct; declined to invent missing info | Grounded, correct; no hallucination once given the document | Both trustworthy on-document |
| Cost / access | Per-request, API key required, rate-limited | Free, no key, no rate limits | — |
| Privacy | Data sent to Google's servers | Inference ran in the notebook runtime | Matters for pharma/clinical documents |
| Context window | Large | Capped at `n_ctx=2048` in this setup | — |

## Test conditions

Three queries against one SDF document. Mistral-7B ran locally on a free T4 GPU. Gemini ran
against the hosted API on the free tier. **Three queries, one document** — the sample is small
and the conclusions are scoped accordingly.

## What else it found

- **Gemini declining to invent is itself a result.** On storage conditions it stated the
  certificate does not specify them rather than filling the gap. That behaviour is what makes
  a model usable on compliance documents.
- **The trust verdict is qualified, not absolute:** grounded on every query, but "I'd still
  want a human to verify anything critical."
- **The `n_ctx=2048` cap is a real constraint** on the local setup and is not a property of
  the model — it's worth reading as a configuration limit rather than a Mistral limitation.
- **The stated surprise:** the expectation was that the cloud model would clearly outperform a
  free local one. It did not.

## Why this matters for the pipeline

This report records the comparison that informed a later notebook configuration using Mistral — otherwise the switch looks arbitrary. The reasoning carried forward:
rate limits at volume, privacy on regulated documents, and a quality gap smaller than the
speed gap. The speed cost this decision carries shows up directly in the
[final pipeline evaluation](final-pipeline-evaluation.md) — about 292 seconds per query on
Mistral-7B, the tradeoff this comparison predicted.
