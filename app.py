from signer.pdf_loader import PDFLoader
from signer.signature_locator import SignatureLocator
from signer.signature_inserter import SignatureInserter
from signer.exporter import PDFExporter

# Load PDF
loader = PDFLoader("assets/sample.pdf")
document = loader.load_pdf()

# Locate signature field
locator = SignatureLocator(document)

location = locator.find_signature_field("Signature")

if location:

    print("Signature field found:", location)

    # Insert signature
    signer = SignatureInserter(document)

    signer.insert_signature(
        page_number=location["page"],
        signature_path="assets/signature.png",
        x=location["x"],
        y=location["y"],
        width=150,
        height=75
    )

    # Export PDF
    exporter = PDFExporter(document)

    saved_path = exporter.save()

    exporter.close()

else:
    print("Signature field not found.")