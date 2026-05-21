import fitz
import tempfile
import os

def sign_pdf(pdf_file, signature_file, page_number, x, y, width=150, height=75):
    pdf_bytes = pdf_file.getvalue()
    signature_bytes = signature_file.getvalue()

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    page_index = page_number - 1

    if page_index < 0 or page_index >= len(doc):
        doc.close()
        raise ValueError("Invalid page number.")

    page = doc[page_index]

    rect = fitz.Rect(x, y, x + width, y + height)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_sig:
        temp_sig.write(signature_bytes)
        temp_sig_path = temp_sig.name

    page.insert_image(rect, filename=temp_sig_path)

    output_bytes = doc.write()
    doc.close()

    os.remove(temp_sig_path)

    return output_bytes
