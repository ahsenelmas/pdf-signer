import fitz  # PyMuPDF


class SignatureLocator:
    def __init__(self, pdf_document):
        self.document = pdf_document

    def find_signature_field(
        self,
        keyword: str = "Signature"
    ):
        """
        Search the PDF for a keyword and return coordinates.

        Returns:
        {
            "page": int,
            "x": float,
            "y": float
        }

        or None if not found.
        """

        try:
            # Loop through all pages
            for page_number in range(len(self.document)):

                page = self.document[page_number]

                # Search for keyword
                matches = page.search_for(keyword)

                if matches:
                    # Take first match
                    rect = matches[0]

                    return {
                        "page": page_number,
                        "x": rect.x1 + 10,  # slightly right of keyword
                        "y": rect.y0 - 20  # slightly above keyword
                    }

            return None

        except Exception as e:
            raise Exception(f"Error locating signature field: {e}")