from signer.pdf_loader import PDFLoader
from signer.signature_locator import SignatureLocator
from signer.signature_inserter import SignatureInserter
from signer.exporter import PDFExporter


def main():

    # Input files
    pdf_path = "assets/sample.pdf"
    signature_path = "assets/signature.png"

    # Load PDF
    loader = PDFLoader(pdf_path)
    document = loader.load_pdf()

    # Find signature location
    locator = SignatureLocator(document)

    location = locator.find_signature_field("Signature")

    if location:

        print("Signature field found:")
        print(location)

        # Insert signature
        signer = SignatureInserter(document)

        signer.insert_signature(
            page_number=location["page"],
            signature_path=signature_path,
            x=location["x"],
            y=location["y"],
            width=150,
            height=75
        )

        # Export signed PDF
        exporter = PDFExporter(document)

        output_path = exporter.save()

        print(f"Signed PDF saved to: {output_path}")

        exporter.close()

    else:
        print("No signature field found in the PDF.")


if __name__ == "__main__":
    main()
