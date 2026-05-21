import os
import tempfile
import fitz
import streamlit as st

from src.detector import detect_signature_text
from src.pdf_signer import sign_pdf


st.set_page_config(
    page_title="PDF Signer",
    page_icon="✍️",
    layout="centered"
)

st.sidebar.title("How to use")
st.sidebar.write("""
1. Upload a PDF file
2. Upload your signature image
3. Check the suggested coordinates
4. Adjust position and signature size if needed
5. Click Generate Signed PDF
6. Preview and download the signed PDF
""")

st.sidebar.info("PDF Signer Internship Project")

if st.sidebar.button("Clear / Reset"):
    st.rerun()


def get_pdf_page_count(pdf_path):
    doc = fitz.open(pdf_path)
    count = len(doc)
    doc.close()
    return count


def preview_pdf_from_bytes(pdf_bytes, page_number=1):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[page_number - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
    img_bytes = pix.tobytes("png")
    doc.close()
    return img_bytes


st.title("✍️ PDF Signer")
st.write("Upload a PDF document and a signature image to sign your file.")

pdf_file = st.file_uploader(
    "Upload PDF File",
    type=["pdf"]
)

suggested_x = 100
suggested_y = 100
suggested_page = 1
page_count = None

if pdf_file is not None:
    file_size_kb = len(pdf_file.getvalue()) / 1024

    st.subheader("PDF Information")
    st.write(f"**File name:** {pdf_file.name}")
    st.write(f"**File size:** {file_size_kb:.2f} KB")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_file.getbuffer())
        temp_pdf_path = temp_pdf.name

    page_count = get_pdf_page_count(temp_pdf_path)
    st.write(f"**Page count:** {page_count}")

    detection_result = detect_signature_text(temp_pdf_path)

    os.remove(temp_pdf_path)

    if detection_result["found"]:
        suggested_page = detection_result["page"]
        suggested_x = int(detection_result["x"])
        suggested_y = int(detection_result["y"])

        st.success(f"Signature text found on page {suggested_page}")
        st.info(f"Suggested coordinates: X={suggested_x}, Y={suggested_y}")
    else:
        st.warning("Signature text not found. Please enter coordinates manually.")

signature_file = st.file_uploader(
    "Upload Signature Image",
    type=["png", "jpg", "jpeg"]
)

if signature_file is not None:
    st.subheader("Signature Preview")
    st.image(signature_file, caption="Uploaded Signature", width=250)

st.subheader("Signature Settings")

col1, col2 = st.columns(2)

with col1:
    page_number = st.number_input(
        "Page Number",
        min_value=1,
        max_value=page_count if page_count else 100,
        value=suggested_page
    )

    x_position = st.number_input(
        "X Position",
        min_value=0,
        value=suggested_x
    )

    signature_width = st.slider(
        "Signature Width",
        min_value=50,
        max_value=400,
        value=150
    )

with col2:
    y_position = st.number_input(
        "Y Position",
        min_value=0,
        value=suggested_y
    )

    signature_height = st.slider(
        "Signature Height",
        min_value=25,
        max_value=200,
        value=75
    )

st.divider()

if st.button("Generate Signed PDF"):
    if pdf_file is None:
        st.error("Please upload a PDF file first.")
    elif signature_file is None:
        st.error("Please upload a signature image first.")
    else:
        try:
            signed_pdf = sign_pdf(
                pdf_file=pdf_file,
                signature_file=signature_file,
                page_number=page_number,
                x=x_position,
                y=y_position,
                width=signature_width,
                height=signature_height
            )

            st.session_state["signed_pdf"] = signed_pdf
            st.session_state["signed_page"] = page_number

        except Exception as e:
            st.error(f"Error while signing PDF: {e}")

if "signed_pdf" in st.session_state:
    st.success("PDF signed successfully.")

    st.subheader("Signed PDF Preview")
    preview_image = preview_pdf_from_bytes(
        st.session_state["signed_pdf"],
        st.session_state["signed_page"]
    )

    st.image(
        preview_image,
        caption="Preview of signed PDF page",
        use_container_width=True
    )

    st.download_button(
        label="Download Signed PDF",
        data=st.session_state["signed_pdf"],
        file_name="signed_document.pdf",
        mime="application/pdf"
    )

st.divider()

st.caption(
    "PDF Signer | Internship Project | Built with Python, Streamlit and PyMuPDF"
)
