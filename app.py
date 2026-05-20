
import streamlit as st

st.set_page_config(
    page_title="PDF Signer",
    page_icon="✍️",
    layout="centered"
)

st.title("PDF Signer")

st.write(
    "Upload a PDF document and a signature image to sign your file."
)

# Upload PDF
pdf_file = st.file_uploader(
    "Upload PDF File",
    type=["pdf"]
)

# Upload signature image
signature_file = st.file_uploader(
    "Upload Signature Image",
    type=["png", "jpg", "jpeg"]
)

# Page number
page_number = st.number_input(
    "Page Number",
    min_value=1,
    value=1
)

# X position
x_position = st.number_input(
    "X Position",
    min_value=0,
    value=100
)

# Y position
y_position = st.number_input(
    "Y Position",
    min_value=0,
    value=100
)

# Sign button
if st.button("Sign PDF"):
    st.success("PDF signing process started!")

# Upload messages
if pdf_file:
    st.info("PDF uploaded successfully!")

if signature_file:
    st.info("Signature uploaded successfully!")

# Download button placeholder
st.download_button(
    label="Download Signed PDF",
    data=b"",
    file_name="signed_document.pdf",
    mime="application/pdf"
)
=======
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