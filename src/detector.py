import fitz

def detect_signature_text(pdf_path):
    doc = fitz.open(pdf_path)

    for page_number in range(len(doc)):
        page = doc[page_number]
        text_instances = page.search_for("Signature")

        if text_instances:
            inst = text_instances[0]
            doc.close()
            return {
                "found": True,
                "page": page_number + 1,
                "x": inst.x0,
                "y": inst.y1 + 10
            }

    doc.close()
    return {
        "found": False,
        "page": None,
        "x": None,
        "y": None
    }
