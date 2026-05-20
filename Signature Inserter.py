import fitz  # PyMuPDF


class SignatureInserter:
    def __init__(self, pdf_document):
        self.document = pdf_document

    def insert_signature(
        self,
        page_number: int,
        signature_path: str,
        x: int,
        y: int,
        width: int = 150,
        height: int = 75
    ):
        """
        Insert signature image into a PDF page.

        Parameters:
        - page_number: Page index (0-based)
        - signature_path: Path to signature image
        - x, y: Position coordinates
        - width, height: Signature size
        """

        try:
            page = self.document[page_number]

            # Define rectangle area for image placement
            rect = fitz.Rect(x, y, x + width, y + height)

            # Insert image
            page.insert_image(rect, filename=signature_path)

            print(f"Signature inserted on page {page_number}")

        except Exception as e:
            raise Exception(f"Error inserting signature: {e}")

    def save_document(self, output_path: str):
        """Save the signed PDF."""
        try:
            self.document.save(output_path)
            print(f"Signed PDF saved at: {output_path}")
        except Exception as e:
            raise Exception(f"Error saving PDF: {e}")

    def close(self):
        """Close the PDF document."""
        self.document.close()