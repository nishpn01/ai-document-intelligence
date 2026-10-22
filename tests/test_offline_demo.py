import unittest
from scripts.offline_demo import PDF, answer, extract_pages


class PublicDemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = extract_pages(PDF)

    def test_selects_requested_certificate_and_field(self):
        result = answer("What lot number is listed on certificate CERT-FIC-101?", self.pages)
        self.assertEqual(result["status"], "answered")
        self.assertEqual(result["pages"], [1])
        self.assertIn("LOT-FIC-ALPHA", result["answer"])

    def test_generic_lot_question_requests_disambiguation(self):
        result = answer("What is the lot number?", self.pages)
        self.assertEqual(result["status"], "clarification-required")
        self.assertIn("CERT-FIC-202", result["answer"])

    def test_scan_page_is_only_read_when_ocr_exists(self):
        expected = "tesseract-ocr" if any(p["method"] == "tesseract-ocr" for p in self.pages) else "ocr-unavailable"
        self.assertEqual(self.pages[2]["method"], expected)


if __name__ == "__main__":
    unittest.main()
