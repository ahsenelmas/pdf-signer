import fitz  # PyMuPDF


class PDFLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.document = None

    def load_pdf(self):
        """Load and validate the PDF file."""
        try:
            self.document = fitz.open(self.file_path)
            return self.document
        except Exception as e:
            raise Exception(f"Error loading PDF: {e}")

    def get_page_count(self) -> int:
        """Return number of pages in the PDF."""
        if self.document is None:
            raise Exception("PDF not loaded. Call load_pdf() first.")
        return len(self.document)

    def get_page(self, page_number: int):
        """Return a specific page."""
        if self.document is None:
            raise Exception("PDF not loaded.")
        
        if page_number < 0 or page_number >= len(self.document):
            raise IndexError("Page number out of range.")
        
        return self.document[page_number]

    def close(self):
        """Close the document."""
        if self.document:
            self.document.close()
