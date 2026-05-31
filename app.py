import io
import os
import tempfile

import fitz
import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas

from db import (
    init_db,
    create_user,
    verify_user,
    save_signed_document,
    get_signed_documents,
    delete_signed_document,
)

from src.detector import detect_signature_text
from src.pdf_signer import sign_pdf


st.set_page_config(page_title="PDF Signer", page_icon="📄", layout="wide")
init_db()


defaults = {
    "user": None,
    "signed_pdf": None,
    "current_x": 100,
    "current_y": 100,
    "current_page": 1,
    "signature_width": 150,
    "signature_height": 75,
    "detection_done": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def auth_page():
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #020617, #111827); color: white; }
    .main .block-container {
        max-width: 520px; margin-top: 5rem; background: rgba(15,23,42,0.95);
        border: 1px solid rgba(148,163,184,0.25); border-radius: 24px;
        padding: 3rem; box-shadow: 0 20px 60px rgba(0,0,0,0.45);
    }
    h1,h2,h3,p,label,span,div { color: white !important; }
    input { border-radius: 8px !important; }
    .stButton > button { border-radius: 10px !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.title("PDF Signer")
    st.write("Login or create an account to continue.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
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


def render_pdf_page(pdf_bytes, page_number=1, zoom=1.5):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc[page_number - 1]
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img_bytes = pix.tobytes("png")
    doc.close()
    return img_bytes


def render_pdf_page_pil(pdf_bytes, page_number=1, zoom=1.5):
    img_bytes = render_pdf_page(pdf_bytes, page_number, zoom)
    return Image.open(io.BytesIO(img_bytes)).convert("RGBA")


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


st.sidebar.title("PDF Signer")
st.sidebar.write("Logged in as:")
st.sidebar.write(st.session_state.user["email"])

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

st.sidebar.divider()

st.sidebar.subheader("Saved Signed PDFs")
saved_docs = get_signed_documents(st.session_state.user["id"])

if saved_docs:
    for doc in saved_docs[:5]:
        col_download, col_delete = st.sidebar.columns([5, 1])

        with col_download:
            st.download_button(
                label=doc["file_name"],
                data=doc["pdf_bytes"],
                file_name=doc["file_name"],
                mime="application/pdf",
                key=f"download_saved_doc_{doc['id']}"
            )

        with col_delete:
            if st.button("🗑️", key=f"delete_saved_doc_{doc['id']}"):
                delete_signed_document(
                    document_id=doc["id"],
                    user_id=st.session_state.user["id"]
                )
                st.sidebar.success("Deleted.")
                st.rerun()
else:
    st.sidebar.caption("No saved signed PDFs yet.")

st.sidebar.divider()

st.sidebar.subheader("Security Note")
st.sidebar.write("""
Signature images are not stored permanently.
They are used only during the signing process.
""")

st.sidebar.divider()

st.sidebar.subheader("How to use")
st.sidebar.write("""
1. Upload a PDF
2. Upload or draw a signature
3. Drag the red box on the PDF preview
4. Click Apply Drag Position
5. Generate signed PDF
6. Download or delete signed PDF
""")

st.sidebar.divider()

if st.sidebar.button("Clear / Reset", key="clear_reset_btn"):
    user = st.session_state.user
    st.session_state.clear()
    st.session_state.user = user
    st.rerun()


st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background:
        linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px),
        radial-gradient(circle at top left, rgba(59,130,246,0.18), transparent 30%),
        radial-gradient(circle at bottom right, rgba(168,85,247,0.16), transparent 30%),
        linear-gradient(to bottom right, #020617, #0f172a);
    background-size: 40px 40px, 40px 40px, auto, auto, auto;
    color: #ffffff;
}

.main .block-container {
    max-width: 1180px;
    background: rgba(15, 23, 42, 0.82);
    border: 1px solid rgba(51,65,85,0.85);
    border-radius: 24px;
    padding: 3rem;
    margin-top: 2rem;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
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
    color: #ffffff !important;
}

.hero p {
    font-size: 1.05rem;
    color: #94a3b8 !important;
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
    padding: 0.65rem 1.15rem !important;
    font-weight: 600 !important;
}

[data-testid="stFileUploader"] {
    background-color: rgba(17,24,39,0.85) !important;
    border: 1px solid #334155 !important;
    border-radius: 14px;
    padding: 12px;
}

[data-testid="stFileUploader"] section {
    background-color: #1e293b !important;
    border: 1px dashed #475569 !important;
    border-radius: 12px;
}

.stAlert { border-radius: 12px; }
input { border-radius: 8px !important; }
canvas { border-radius: 14px !important; }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <h1>PDF Signer</h1>
    <p>Upload, preview, sign, and download PDFs without permanently storing signature images.</p>
</div>
""", unsafe_allow_html=True)


st.info(
    "For security reasons, signature images are not stored permanently. "
    "They are only used temporarily during the signing process."
)

pdf_file = st.file_uploader("Upload PDF File", type=["pdf"], key="pdf_uploader")

signature_source = st.radio(
    "Signature Method",
    ["Upload Signature Image", "Draw Signature"],
    horizontal=True,
    key="signature_method"
)

active_signature_bytes = None


if signature_source == "Upload Signature Image":
    signature_file = st.file_uploader(
        "Upload Signature Image",
        type=["png", "jpg", "jpeg"],
        key="signature_uploader"
    )

    if signature_file:
        active_signature_bytes = signature_file.getvalue()
        st.image(signature_file, caption="Uploaded Signature - temporary only", width=250)

elif signature_source == "Draw Signature":
    st.subheader("Draw Your Signature")
    st.write("Draw inside the white box below:")

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

    if st.button("Clear Drawing", key="clear_drawing_btn"):
        st.session_state.pop("signature_canvas", None)
        st.rerun()


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

    try:
        os.remove(temp_pdf_path)
    except Exception:
        pass

    if detection_result["found"] and not st.session_state.detection_done:
        st.session_state.current_page = detection_result["page"]
        st.session_state.current_x = int(detection_result["x"])
        st.session_state.current_y = int(detection_result["y"])
        st.session_state.detection_done = True

    if detection_result["found"]:
        st.success(f"Signature text found on page {detection_result['page']}")
        st.info(
            f"Suggested coordinates: X={int(detection_result['x'])}, "
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

    st.subheader("Drag Signature Position")

    if active_signature_bytes:
        st.write("Drag the red box on the PDF preview, then click **Apply Drag Position**.")

        canvas_zoom = 1.5
        bg_img = render_pdf_page_pil(pdf_bytes, st.session_state.current_page, zoom=canvas_zoom)
        canvas_width, canvas_height = bg_img.size

        initial_drawing = {
            "version": "4.4.0",
            "objects": [
                {
                    "type": "rect",
                    "left": st.session_state.current_x * canvas_zoom,
                    "top": st.session_state.current_y * canvas_zoom,
                    "width": st.session_state.signature_width * canvas_zoom,
                    "height": st.session_state.signature_height * canvas_zoom,
                    "fill": "rgba(239, 68, 68, 0.18)",
                    "stroke": "#ef4444",
                    "strokeWidth": 2,
                    "rx": 6,
                    "ry": 6,
                }
            ],
        }

        drag_canvas = st_canvas(
            fill_color="rgba(239, 68, 68, 0.18)",
            stroke_width=2,
            stroke_color="#ef4444",
            background_image=bg_img,
            height=canvas_height,
            width=canvas_width,
            drawing_mode="transform",
            initial_drawing=initial_drawing,
            update_streamlit=True,
            key=f"drag_canvas_page_{st.session_state.current_page}"
        )

        if st.button("Apply Drag Position", key="apply_drag_position_btn"):
            try:
                objects = drag_canvas.json_data["objects"]

                if objects:
                    obj = objects[0]
                    left = obj.get("left", 0)
                    top = obj.get("top", 0)
                    width = obj.get("width", st.session_state.signature_width * canvas_zoom)
                    height = obj.get("height", st.session_state.signature_height * canvas_zoom)
                    scale_x = obj.get("scaleX", 1)
                    scale_y = obj.get("scaleY", 1)

                    st.session_state.current_x = int(left / canvas_zoom)
                    st.session_state.current_y = int(top / canvas_zoom)
                    st.session_state.signature_width = int((width * scale_x) / canvas_zoom)
                    st.session_state.signature_height = int((height * scale_y) / canvas_zoom)

                    st.success("Signature position updated.")
                    st.rerun()
                else:
                    st.warning("Please move the red signature box first.")
            except Exception as e:
                st.error(f"Could not read drag position: {e}")

        st.subheader("Live Preview with Signature")

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

            preview_img = render_pdf_page(preview_pdf, st.session_state.current_page)

            st.image(
                preview_img,
                caption="Live Preview with Signature",
                use_column_width=True
            )
        except Exception as e:
            st.warning(f"Live preview could not be generated: {e}")

    else:
        st.subheader("PDF Page Preview")
        preview_img = render_pdf_page(pdf_bytes, st.session_state.current_page)

        st.image(
            preview_img,
            caption=f"Page {st.session_state.current_page}",
            use_column_width=True
        )

    st.subheader("Adjust Signature Position")
    st.info(
        "Recommended: first drag the red box and click Apply Drag Position. "
        "Use the arrows only for small final adjustments."
    )

    move_step = st.slider(
        "Move step",
        min_value=1,
        max_value=50,
        value=10,
        key="move_step_slider"
    )

    col_left, col_up, col_down, col_right, col_reset = st.columns(5)

    with col_left:
        if st.button("← Left", key="move_left_btn"):
            st.session_state.current_x -= move_step
            st.rerun()

    with col_up:
        if st.button("↑ Up", key="move_up_btn"):
            st.session_state.current_y -= move_step
            st.rerun()

    with col_down:
        if st.button("↓ Down", key="move_down_btn"):
            st.session_state.current_y += move_step
            st.rerun()

    with col_right:
        if st.button("→ Right", key="move_right_btn"):
            st.session_state.current_x += move_step
            st.rerun()

    with col_reset:
        if st.button("Reset Position", key="reset_position_btn"):
            if detection_result["found"]:
                st.session_state.current_x = int(detection_result["x"])
                st.session_state.current_y = int(detection_result["y"])
                st.session_state.current_page = detection_result["page"]
            else:
                st.session_state.current_x = 100
                st.session_state.current_y = 100
            st.rerun()

    st.write(
        f"Current position: X={st.session_state.current_x}, "
        f"Y={st.session_state.current_y}, "
        f"Width={st.session_state.signature_width}, "
        f"Height={st.session_state.signature_height}"
    )

    with st.expander("Advanced Signature Settings"):
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
            st.error("Please upload or draw a signature.")
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

                save_signed_document(
                    user_id=st.session_state.user["id"],
                    file_name=f"signed_{pdf_file.name}",
                    pdf_bytes=signed_pdf
                )

                active_signature_bytes = None

                st.success("PDF signed successfully. The signature image was not stored permanently.")
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
            use_column_width=True
        )

        st.download_button(
            label="Download Signed PDF",
            data=st.session_state.signed_pdf,
            file_name="signed_document.pdf",
            mime="application/pdf",
            key="download_signed_pdf_btn"
        )


st.divider()
st.caption("PDF Signer | Internship Project | Python · Streamlit · PyMuPDF · Neon PostgreSQL")
