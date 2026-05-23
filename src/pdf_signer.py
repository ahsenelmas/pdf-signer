import fitz

def sign_pdf(pdf_file, signature_file, page_number, x, y, width=150, height=75):
    pdf_bytes = pdf_file.getvalue()
    signature_bytes = signature_file.getvalue()

    if not signature_bytes:
        raise ValueError("Signature image is empty.")

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        page_index = page_number - 1

        if page_index < 0 or page_index >= len(doc):
            raise ValueError("Invalid page number.")

        page = doc[page_index]
        rect = fitz.Rect(x, y, x + width, y + height)
        page.insert_image(rect, stream=signature_bytes)

        return doc.write()
    finally:
        doc.close()
