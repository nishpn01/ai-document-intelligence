"""Small deterministic extraction and retrieval check; not an LLM evaluation."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import tempfile
import time
import fitz

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "data/public-fixtures/synthetic-quality-documents.pdf"
KEY = ROOT / "data/public-fixtures/answer-key.json"


def extract_pages(pdf_path):
    pages = []
    with fitz.open(pdf_path) as pdf:
        for number, page in enumerate(pdf):
            text = page.get_text().strip()
            method = "pdf-text"
            if not text and shutil.which("tesseract"):
                with tempfile.NamedTemporaryFile(suffix=".png") as img:
                    page.get_pixmap(matrix=fitz.Matrix(2, 2)).save(img.name)
                    proc = subprocess.run(["tesseract", img.name, "stdout"], capture_output=True, text=True, check=True)
                    text, method = proc.stdout.strip(), "tesseract-ocr"
            elif not text:
                method = "ocr-unavailable"
            pages.append({"page": number + 1, "text": text, "method": method})
    return pages


def retrieve(question, pages):
    # Intentionally tiny lexical baseline for a public offline demonstration.
    terms = set(re.findall(r"[a-z0-9]+", question.lower())) - {"what", "is", "the", "for", "which", "a", "an", "of"}
    ranked = sorted(((sum(t in p["text"].lower() for t in terms), p) for p in pages), key=lambda x: (-x[0], x[1]["page"]))
    return [p for score, p in ranked if score > 0][:3]


def answer(question, pages):
    selected = retrieve(question, pages)
    if re.search(r"\blot\b", question, re.I) and not re.search(r"CERT-FIC-(101|202)\b", question, re.I):
        return {"status": "clarification-required", "pages": [p["page"] for p in selected], "answer": "Which certificate do you mean: CERT-FIC-101 or CERT-FIC-202?"}
    for p in selected:
        for line in p["text"].splitlines():
            if _matches_question(line, question):
                return {"status": "answered", "pages": [p["page"]], "answer": line.strip()}
    return {"status": "not-found", "pages": [p["page"] for p in selected], "answer": "No matching field was found in the retrieved text."}


def _matches_question(line, question):
    q = question.lower()
    field = line.split(":", 1)[0].lower()
    if field == "lot number": return "lot" in q
    if field == "expiration date": return "expiration" in q or "expiry" in q
    if field == "product": return "product" in q
    if field == "certificate id": return "certificate id" in q or "certificate identifier" in q
    return field == "record id" and "record id" in q


def run():
    started = time.monotonic()
    pages = extract_pages(PDF)
    key = json.loads(KEY.read_text())
    checks = []
    for case in key["questions"]:
        got = answer(case["question"], pages)
        expect = case["expected_answer"]
        if case.get("requires_ocr") and not any(p["method"] == "tesseract-ocr" for p in pages):
            got = {"status": "skipped-ocr-unavailable", "pages": [], "answer": "OCR check skipped: tesseract is unavailable."}
        actual_text = got["answer"].lower()
        skipped = got["status"] == "skipped-ocr-unavailable"
        passed = "skipped" if skipped else (
            (case["expected_page"] is None or case["expected_page"] in got["pages"]) and
            all(token.lower() in actual_text for token in expect.get("contains", [])) and got["status"] == expect["status"]
        )
        checks.append({"id": case["id"], "passed": passed, "expected_page": case["expected_page"], **got})
    result = {
        "run_type": "deterministic lexical demo; not original embedding/LLM evaluation",
        "pdf": PDF.name,
        "page_count": len(pages),
        "extraction": [{"page": p["page"], "method": p["method"], "characters": len(p["text"])} for p in pages],
        "ocr_available": bool(shutil.which("tesseract")),
        "checks": checks,
        "passed": all(c["passed"] is not False for c in checks),
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    out = ROOT / "data/public-fixtures/offline-checks.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    assert result["passed"], "One or more public fixture checks failed"


if __name__ == "__main__":
    run()
