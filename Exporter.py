import os
from datetime import datetime


class PDFExporter:
    def __init__(self, pdf_document):
        self.document = pdf_document

    def generate_output_path(
        self,
        output_dir: str = "output",
        filename_prefix: str = "signed"
    ) -> str:
        """
        Generate a unique output file path using timestamp.
        """

        # Create output folder if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"{filename_prefix}_{timestamp}.pdf"

        return os.path.join(output_dir, filename)

    def save(self, output_path: str = None):
        """
        Save the PDF document.
        """

        try:

            # Auto-generate path if none provided
            if output_path is None:
                output_path = self.generate_output_path()

            self.document.save(output_path)

            print(f"PDF successfully saved to:\n{output_path}")

            return output_path

        except Exception as e:
            raise Exception(f"Error exporting PDF: {e}")

    def close(self):
        """
        Close the PDF document.
        """

        if self.document:
            self.document.close()