from pathlib import Path

import fitz
from PIL import Image

from src.detector import detect_signature_text
from src.pdf_signer import sign_pdf


def _create_pdf(path: Path, pages: int = 1, text: str = "") -> None:
    doc = fitz.open()

    for _ in range(pages):
        page = doc.new_page()
        if text:
            page.insert_text((72, 72), text, fontsize=18)

    doc.save(path)
    doc.close()


def _create_signature_image(path: Path, format_name: str = "JPEG") -> None:
    image = Image.new("RGB", (220, 90), color=(20, 90, 200))
    image.save(path, format=format_name)


def test_detect_signature_text_finds_hint(tmp_path):
    pdf_path = tmp_path / "with_signature_hint.pdf"
    _create_pdf(pdf_path, pages=2, text="Signature")

    result = detect_signature_text(str(pdf_path))

    assert result["found"] is True
    assert result["page"] == 1
    assert result["x"] is not None
    assert result["y"] is not None


def test_sign_pdf_inserts_signature_from_jpeg_stream(tmp_path):
    pdf_path = tmp_path / "input.pdf"
    signature_path = tmp_path / "signature.jpg"
    _create_pdf(pdf_path, pages=1, text="Please sign here")
    _create_signature_image(signature_path, format_name="JPEG")

    signed_bytes = sign_pdf(
        pdf_file=type("PdfFile", (), {"getvalue": lambda self: pdf_path.read_bytes()})(),
        signature_file=type("SignatureFile", (), {"getvalue": lambda self: signature_path.read_bytes()})(),
        page_number=1,
        x=110,
        y=130,
        width=160,
        height=70,
    )

    doc = fitz.open(stream=signed_bytes, filetype="pdf")
    page = doc[0]
    images = page.get_images(full=True)
    doc.close()

    assert len(images) == 1


def test_sign_pdf_rejects_invalid_page_number(tmp_path):
    pdf_path = tmp_path / "input.pdf"
    signature_path = tmp_path / "signature.png"
    _create_pdf(pdf_path, pages=1, text="Please sign here")
    _create_signature_image(signature_path, format_name="PNG")

    try:
        sign_pdf(
            pdf_file=type("PdfFile", (), {"getvalue": lambda self: pdf_path.read_bytes()})(),
            signature_file=type("SignatureFile", (), {"getvalue": lambda self: signature_path.read_bytes()})(),
            page_number=2,
            x=110,
            y=130,
            width=160,
            height=70,
        )
    except ValueError as error:
        assert str(error) == "Invalid page number."
    else:
        raise AssertionError("Expected ValueError for an invalid page number.")