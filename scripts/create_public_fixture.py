"""Create the fictional PDF used by the public offline demo."""
from pathlib import Path
import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data/public-fixtures/synthetic-quality-documents.pdf"


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    for title, cert, lot, product, date in [
        ("QUALITY CERTIFICATE", "CERT-FIC-101", "LOT-FIC-ALPHA", "Fictional Buffer Kit", "2031-04-15"),
        ("QUALITY CERTIFICATE", "CERT-FIC-202", "LOT-FIC-BRAVO", "Fictional Filter Set", "2032-09-30"),
    ]:
        page = doc.new_page()
        page.insert_text((60, 70), "SAMPLE ONLY — FICTIONAL DATA", fontsize=16)
        page.insert_text((60, 115), title, fontsize=20)
        page.insert_text((60, 155), f"Certificate ID: {cert}", fontsize=13)
        page.insert_text((60, 180), f"Product: {product}", fontsize=13)
        page.insert_text((60, 205), f"Lot number: {lot}", fontsize=13)
        page.insert_text((60, 230), f"Expiration date: {date}", fontsize=13)
        page.insert_text((60, 270), "Storage: Keep between 2 and 8 degrees C.", fontsize=12)
    # Render a third page as an image so it has no selectable text layer.
    image = Image.new("RGB", (1240, 1754), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=36)
    small = ImageFont.load_default(size=30)
    for y, line, f in [(170, "SAMPLE ONLY - FICTIONAL DATA", font), (270, "SCANNED INSPECTION RECORD", font), (390, "Record ID: REC-FIC-303", small), (455, "Inspection result: PASS", small), (520, "Inspector: Fictional Sample", small)]:
        draw.text((100, y), line, fill="black", font=f)
    page = doc.new_page(width=620, height=877)
    # PNG embedding preserves the scan-only page while keeping the generator simple.
    import io
    page.insert_image(page.rect, stream=io.BytesIO(_png(image)))
    doc.save(OUTPUT, garbage=4, deflate=True)
    doc.close()
    print(OUTPUT)


def _png(image):
    import io
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


if __name__ == "__main__":
    main()
