import fitz

def detect_signature_text(pdf_path):
    doc = fitz.open(pdf_path)

    for page_number in range(len(doc)):
        page = doc[page_number]

        text_instances = page.search_for("Signature")

        if text_instances:
            for inst in text_instances:
                print(f"Found on page {page_number + 1}")
                print(f"Coordinates: {inst}")

        else:
            print("No signature text found")


pdf_file = "sample.pdf"

detect_signature_text(pdf_file)