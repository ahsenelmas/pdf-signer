from pathlib import Path

from src.detector import detect_signature_text
from src.pdf_signer import sign_pdf


ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "sample" / "sample.pdf"
SIGNATURE_PATH = ROOT / "sample" / "download.png"
OUTPUT_PATH = ROOT / "output" / "signed_demo.pdf"


def _buffer_from_path(path: Path):
    return type("Buffer", (), {"getvalue": lambda self: path.read_bytes()})()


def main() -> None:
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Sample PDF not found: {PDF_PATH}")

    if not SIGNATURE_PATH.exists():
        raise FileNotFoundError(f"Sample signature image not found: {SIGNATURE_PATH}")

    detection = detect_signature_text(str(PDF_PATH))
    page_number = detection["page"] if detection["found"] else 1
    x_position = int(detection["x"]) if detection["found"] and detection["x"] is not None else 100
    y_position = int(detection["y"]) if detection["found"] and detection["y"] is not None else 100

    signed_bytes = sign_pdf(
        pdf_file=_buffer_from_path(PDF_PATH),
        signature_file=_buffer_from_path(SIGNATURE_PATH),
        page_number=page_number,
        x=x_position,
        y=y_position,
        width=180,
        height=80,
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(signed_bytes)

    print(f"Signed demo created: {OUTPUT_PATH}")
    print(f"Used page {page_number} at X={x_position}, Y={y_position}")


if __name__ == "__main__":
    main()