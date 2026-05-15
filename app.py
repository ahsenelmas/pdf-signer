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

pdf_file = st.file_uploader(
    "Upload PDF File",
    type=["pdf"]
)

signature_file = st.file_uploader(
    "Upload Signature Image",
    type=["png", "jpg", "jpeg"]
)

page_number = st.number_input(
    "Page Number",
    min_value=1,
    value=1
)

x_position = st.number_input(
    "X Position",
    min_value=0,
    value=100
)

y_position = st.number_input(
    "Y Position",
    min_value=0,
    value=100
)

if st.button("Sign PDF"):
    st.success("PDF signing process started!")

if pdf_file:
    st.info("PDF uploaded successfully!")

if signature_file:
    st.info("Signature uploaded successfully!")
