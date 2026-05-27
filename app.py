import io
import os
import tempfile

import fitz
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

from src.detector import detect_signature_text
from src.pdf_signer import sign_pdf
from db import init_db, create_user, verify_user


st.set_page_config(
    page_title="PDF Signer",
    page_icon="📄",
    layout="wide"
)

init_db()

if "user" not in st.session_state:
    st.session_state.user = None


def auth_page():
    st.title("PDF Signer Authentication")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        st.subheader("Login")

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            user = verify_user(email, password)

            if user:
                st.session_state.user = user
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid email or password.")

    with register_tab:
        st.subheader("Create Account")

        full_name = st.text_input("Full Name", key="register_full_name")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")

        if st.button("Register"):
            if not email or not password:
                st.warning("Please enter email and password.")
            else:
                try:
                    create_user(email, password, full_name)
                    st.success("Account created. You can login now.")
                except Exception:
                    st.error("This email is already registered or database error occurred.")


if st.session_state.user is None:
    auth_page()
    st.stop()

# ---------- SESSION ----------
defaults = {
    "signed_pdf": None,
    "current_x": 100,
    "current_y": 100,
    "current_page": 1,
    "signature_width": 150,
    "signature_height": 75,
    "signature_templates": {},
    "detection_done": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- HELPERS ----------
def render_pdf_page(pdf_bytes, page_number=1, zoom=1.5):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[page_number - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img_bytes = pix.tobytes("png")
    doc.close()
    return img_bytes


def get_pdf_page_count(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    count = len(doc)
    doc.close()
    return count


def save_uploaded_file(uploaded_file, suffix):
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return temp_file.name


def draw_signature_to_png(canvas_result):
    if canvas_result.image_data is None:
        return None

    image = Image.fromarray(canvas_result.image_data.astype("uint8"), "RGBA")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def create_preview_with_signature(pdf_bytes, signature_bytes, page_number, x, y, width, height):
    return sign_pdf(
        pdf_file=io.BytesIO(pdf_bytes),
        signature_file=io.BytesIO(signature_bytes),
        page_number=page_number,
        x=x,
        y=y,
        width=width,
        height=height
    )


# ---------- SIDEBAR ----------
st.sidebar.title("PDF Signer")

st.sidebar.write(f"Logged in as: {st.session_state.user['email']}")

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

theme = st.sidebar.radio(
    "Theme",
    ["Dark", "Light"],
    index=0,
    key="theme_selector"
)

st.sidebar.divider()

st.sidebar.subheader("How to use")
st.sidebar.write("""
1. Upload a PDF
2. Upload or draw a signature
3. Signature appears automatically
4. Move it with direction buttons
5. Generate signed PDF
6. Preview and download
""")

st.sidebar.divider()

if st.sidebar.button("Clear / Reset", key="clear_reset_btn"):
    st.session_state.clear()
    st.rerun()


# ---------- STYLE ----------
st.markdown("""
<style>
.main .block-container {
    max-width: 1180px;
    padding-top: 3rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 2rem 0 1.5rem 0;
    border-bottom: 1px solid rgba(148, 163, 184, 0.25);
    margin-bottom: 2rem;
}

.hero h1 {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    margin-bottom: 0.4rem;
}

.hero p {
    font-size: 1.05rem;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 10px !important;
    padding: 0.6rem 1.1rem !important;
    font-weight: 600 !important;
}

[data-testid="stFileUploader"] {
    border-radius: 14px;
}

.stAlert {
    border-radius: 12px;
}

input {
    border-radius: 8px !important;
}

iframe {
    width: 520px !important;
    max-width: 520px !important;
    background-color: white !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)


if theme == "Light":
    st.markdown("""
    <style>
    .stApp {
        background-image:
            linear-gradient(rgba(15,23,42,0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(15,23,42,0.035) 1px, transparent 1px),
            radial-gradient(circle at top left, rgba(59,130,246,0.12), transparent 30%),
            radial-gradient(circle at bottom right, rgba(168,85,247,0.12), transparent 30%),
            linear-gradient(to bottom right, #f8fafc, #e2e8f0);
        background-size: 40px 40px, 40px 40px, auto, auto, auto;
        color: #0f172a;
    }

    .main .block-container {
        background: rgba(255,255,255,0.82);
        backdrop-filter: blur(18px);
        border: 1px solid rgba(203,213,225,0.75);
        border-radius: 24px;
        padding: 3rem;
        margin-top: 2rem;
        box-shadow: 0 20px 50px rgba(15, 23, 42, 0.12);
    }

    h1, h2, h3, h4, p, label, span {
        color: #0f172a !important;
    }

    .hero p {
        color: #64748b !important;
    }

    [data-testid="stFileUploader"] {
        background-color: rgba(255,255,255,0.85) !important;
        border: 1px solid #d1d5db !important;
        padding: 12px;
    }

    [data-testid="stFileUploader"] section {
        background-color: #f8fafc !important;
        border: 1px dashed #94a3b8 !important;
        border-radius: 12px;
    }

    [data-testid="stFileUploader"] button,
    .stButton > button,
    .stDownloadButton > button {
        background-color: #1e40af !important;
        color: white !important;
    }

    input {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <style>
    .stApp {
        background-image:
            linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px),
            radial-gradient(circle at top left, rgba(59,130,246,0.18), transparent 30%),
            radial-gradient(circle at bottom right, rgba(168,85,247,0.16), transparent 30%),
            linear-gradient(to bottom right, #020617, #0f172a);
        background-size: 40px 40px, 40px 40px, auto, auto, auto;
        color: #ffffff;
    }

    .main .block-container {
        background: rgba(15, 23, 42, 0.82);
        backdrop-filter: blur(18px);
        border: 1px solid rgba(51,65,85,0.85);
        border-radius: 24px;
        padding: 3rem;
        margin-top: 2rem;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
    }

    .hero h1 {
        color: #ffffff !important;
    }

    .hero p {
        color: #94a3b8 !important;
    }

    [data-testid="stFileUploader"] {
        background-color: rgba(17,24,39,0.85) !important;
        border: 1px solid #334155 !important;
        padding: 12px;
    }

    [data-testid="stFileUploader"] section {
        background-color: #1e293b !important;
        border: 1px dashed #475569 !important;
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)


# ---------- MAIN ----------
st.markdown("""
<div class="hero">
    <h1>PDF Signer</h1>
    <p>Securely upload, preview, place signatures, and download signed PDF documents.</p>
</div>
""", unsafe_allow_html=True)


pdf_file = st.file_uploader(
    "Upload PDF File",
    type=["pdf"],
    key="pdf_uploader"
)

signature_source = st.radio(
    "Signature Method",
    ["Upload Signature Image", "Draw Signature"],
    horizontal=True,
    key="signature_method"
)

signature_file = None
drawn_signature = None
active_signature_bytes = None


# ---------- SIGNATURE INPUT ----------
if signature_source == "Upload Signature Image":
    signature_file = st.file_uploader(
        "Upload Signature Image",
        type=["png", "jpg", "jpeg"],
        key="signature_uploader"
    )

    if signature_file:
        active_signature_bytes = signature_file.getvalue()
        st.image(signature_file, caption="Uploaded Signature", width=250)

        template_name = st.text_input(
            "Save this signature as template",
            placeholder="Example: My Signature",
            key="uploaded_signature_template_name"
        )

        if st.button("Save Signature Template", key="save_uploaded_signature_template_btn"):
            if template_name:
                st.session_state.signature_templates[template_name] = active_signature_bytes
                st.success("Signature template saved.")
            else:
                st.warning("Please enter a template name.")

else:
    st.subheader("Draw Your Signature")
    st.write("Draw inside the white box below:")

    canvas_col, empty_col = st.columns([1, 2])

    with canvas_col:
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=3,
            stroke_color="#000000",
            background_color="#ffffff",
            height=180,
            width=500,
            drawing_mode="freedraw",
            update_streamlit=True,
            key="signature_canvas"
        )

    drawn_signature = draw_signature_to_png(canvas_result)

    if drawn_signature:
        active_signature_bytes = drawn_signature.getvalue()

    col_clear, col_save = st.columns([1, 3])

    with col_clear:
        if st.button("Clear Drawing", key="clear_drawing_btn"):
            st.session_state.pop("signature_canvas", None)
            st.rerun()

    with col_save:
        template_name = st.text_input(
            "Save drawn signature as template",
            placeholder="Example: My Signature",
            key="drawn_signature_template_name"
        )

        if st.button("Save Drawn Signature Template", key="save_drawn_signature_template_btn"):
            if template_name and active_signature_bytes:
                st.session_state.signature_templates[template_name] = active_signature_bytes
                st.success("Drawn signature template saved.")
            else:
                st.warning("Please draw a signature and enter a template name.")


# ---------- TEMPLATE ----------
selected_template = "None"

if st.session_state.signature_templates:
    selected_template = st.selectbox(
        "Use saved signature template",
        ["None"] + list(st.session_state.signature_templates.keys()),
        key="template_selector"
    )

    if selected_template != "None":
        active_signature_bytes = st.session_state.signature_templates[selected_template]

        st.image(
            active_signature_bytes,
            caption=f"Template: {selected_template}",
            width=250
        )


# ---------- PDF AREA ----------
if pdf_file:
    pdf_bytes = pdf_file.getvalue()
    page_count = get_pdf_page_count(pdf_bytes)

    st.subheader("PDF Information")

    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        st.write(f"**File name:** {pdf_file.name}")

    with col_info2:
        st.write(f"**File size:** {len(pdf_bytes) / 1024:.2f} KB")

    with col_info3:
        st.write(f"**Pages:** {page_count}")

    temp_pdf_path = save_uploaded_file(pdf_file, ".pdf")
    detection_result = detect_signature_text(temp_pdf_path)
    os.remove(temp_pdf_path)

    if detection_result["found"] and not st.session_state.detection_done:
        st.session_state.current_page = detection_result["page"]
        st.session_state.current_x = int(detection_result["x"])
        st.session_state.current_y = int(detection_result["y"])
        st.session_state.detection_done = True

    if detection_result["found"]:
        st.success(f"Signature text found on page {detection_result['page']}")
        st.info(
            f"Suggested coordinates: "
            f"X={int(detection_result['x'])}, "
            f"Y={int(detection_result['y'])}"
        )
    else:
        st.warning("Signature text not found. Default position is used.")

    st.session_state.current_page = st.number_input(
        "Preview Page",
        min_value=1,
        max_value=page_count,
        value=st.session_state.current_page,
        key="preview_page_input"
    )

    st.subheader("PDF Page Preview")

    if active_signature_bytes:
        try:
            preview_pdf = create_preview_with_signature(
                pdf_bytes=pdf_bytes,
                signature_bytes=active_signature_bytes,
                page_number=st.session_state.current_page,
                x=st.session_state.current_x,
                y=st.session_state.current_y,
                width=st.session_state.signature_width,
                height=st.session_state.signature_height
            )

            preview_img = render_pdf_page(
                preview_pdf,
                st.session_state.current_page
            )

            st.image(
                preview_img,
                caption="Live Preview with Signature",
                width="stretch"
            )

        except Exception as e:
            st.warning(f"Live preview could not be generated: {e}")

            preview_img = render_pdf_page(
                pdf_bytes,
                st.session_state.current_page
            )

            st.image(
                preview_img,
                caption=f"Page {st.session_state.current_page}",
                width="stretch"
            )

    else:
        preview_img = render_pdf_page(
            pdf_bytes,
            st.session_state.current_page
        )

        st.image(
            preview_img,
            caption=f"Page {st.session_state.current_page}",
            width="stretch"
        )

    st.subheader("Adjust Signature Position")

    move_step = st.slider(
        "Move step",
        min_value=1,
        max_value=50,
        value=10,
        key="move_step_slider"
    )

    col_a, col_b, col_c, col_d, col_e = st.columns([1, 1, 1, 1, 1])

    with col_b:
        if st.button("Up", key="move_up_btn"):
            st.session_state.current_y -= move_step
            st.rerun()

    with col_a:
        if st.button("Left", key="move_left_btn"):
            st.session_state.current_x -= move_step
            st.rerun()

    with col_c:
        if st.button("Down", key="move_down_btn"):
            st.session_state.current_y += move_step
            st.rerun()

    with col_d:
        if st.button("Right", key="move_right_btn"):
            st.session_state.current_x += move_step
            st.rerun()

    with col_e:
        if st.button("Reset Position", key="reset_position_btn"):
            if detection_result["found"]:
                st.session_state.current_x = int(detection_result["x"])
                st.session_state.current_y = int(detection_result["y"])
                st.session_state.current_page = detection_result["page"]
            else:
                st.session_state.current_x = 100
                st.session_state.current_y = 100
            st.rerun()

    st.subheader("Signature Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.session_state.current_x = st.number_input(
            "X Position",
            min_value=0,
            value=st.session_state.current_x,
            key="x_position_input"
        )

        st.session_state.signature_width = st.slider(
            "Signature Width",
            min_value=50,
            max_value=400,
            value=st.session_state.signature_width,
            key="signature_width_slider"
        )

    with col2:
        st.session_state.current_y = st.number_input(
            "Y Position",
            min_value=0,
            value=st.session_state.current_y,
            key="y_position_input"
        )

        st.session_state.signature_height = st.slider(
            "Signature Height",
            min_value=25,
            max_value=200,
            value=st.session_state.signature_height,
            key="signature_height_slider"
        )

    st.divider()

    if st.button("Generate Signed PDF", key="generate_signed_pdf_btn"):
        if not active_signature_bytes:
            st.error("Please upload, draw, or select a signature.")
        else:
            try:
                signed_pdf = sign_pdf(
                    pdf_file=io.BytesIO(pdf_bytes),
                    signature_file=io.BytesIO(active_signature_bytes),
                    page_number=st.session_state.current_page,
                    x=st.session_state.current_x,
                    y=st.session_state.current_y,
                    width=st.session_state.signature_width,
                    height=st.session_state.signature_height
                )

                st.session_state.signed_pdf = signed_pdf
                st.success("PDF signed successfully.")

            except Exception as e:
                st.error(f"Error while signing PDF: {e}")

    if st.session_state.signed_pdf:
        st.subheader("Signed PDF Preview")

        signed_preview = render_pdf_page(
            st.session_state.signed_pdf,
            st.session_state.current_page
        )

        st.image(
            signed_preview,
            caption="Signed PDF Preview",
            width="stretch"
        )

        st.download_button(
            label="Download Signed PDF",
            data=st.session_state.signed_pdf,
            file_name="signed_document.pdf",
            mime="application/pdf",
            key="download_signed_pdf_btn"
        )


st.divider()
st.caption("PDF Signer | Internship Project | Python · Streamlit · PyMuPDF")
