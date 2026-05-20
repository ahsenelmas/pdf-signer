import streamlit as st
from detector import detect_signature_text

st.set_page_config(
    page_title="PDF Signer",
    page_icon="✍️",
    layout="centered"
)

st.title("PDF Signer")

st.write("Upload a PDF document and a signature image to sign your file.")

# Upload PDF
pdf_file = st.file_uploader(
    "Upload PDF File",
    type=["pdf"]
)

# Automatic signature coordinate suggestion
if pdf_file is not None:
    with open("temp_uploaded.pdf", "wb") as f:
        f.write(pdf_file.getbuffer())

    detection_result = detect_signature_text("temp_uploaded.pdf")

    if detection_result["found"]:
        st.success(f"Signature text found on page {detection_result['page']}")
        st.info(
            f"Suggested coordinates: "
            f"X={detection_result['x']:.2f}, "
            f"Y={detection_result['y']:.2f}"
        )
    else:
        st.warning("Signature text not found. Please enter coordinates manually.")

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