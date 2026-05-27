import os
import base64
import bcrypt
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is missing.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS signature_templates (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                template_name TEXT NOT NULL,
                signature_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS signed_documents (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                file_name TEXT NOT NULL,
                pdf_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))


def create_user(email, password, full_name=""):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO users (email, password_hash, full_name)
                VALUES (:email, :password_hash, :full_name)
            """),
            {
                "email": email,
                "password_hash": password_hash,
                "full_name": full_name
            }
        )


def verify_user(email, password):
    with engine.begin() as conn:
        user = conn.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": email}
        ).mappings().first()

    if not user:
        return None

    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return dict(user)

    return None


def save_signature_template(user_id, template_name, signature_bytes):
    signature_base64 = base64.b64encode(signature_bytes).decode("utf-8")

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO signature_templates
                (user_id, template_name, signature_data)
                VALUES (:user_id, :template_name, :signature_data)
            """),
            {
                "user_id": user_id,
                "template_name": template_name,
                "signature_data": signature_base64
            }
        )


def get_signature_templates(user_id):
    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                SELECT id, template_name, signature_data, created_at
                FROM signature_templates
                WHERE user_id = :user_id
                ORDER BY created_at DESC
            """),
            {"user_id": user_id}
        ).mappings().all()

    templates = []
    for row in rows:
        templates.append({
            "id": row["id"],
            "template_name": row["template_name"],
            "signature_bytes": base64.b64decode(row["signature_data"]),
            "created_at": row["created_at"]
        })

    return templates


def delete_signature_template(template_id, user_id):
    with engine.begin() as conn:
        conn.execute(
            text("""
                DELETE FROM signature_templates
                WHERE id = :template_id AND user_id = :user_id
            """),
            {
                "template_id": template_id,
                "user_id": user_id
            }
        )


def save_signed_document(user_id, file_name, pdf_bytes):
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO signed_documents
                (user_id, file_name, pdf_data)
                VALUES (:user_id, :file_name, :pdf_data)
            """),
            {
                "user_id": user_id,
                "file_name": file_name,
                "pdf_data": pdf_base64
            }
        )


def get_signed_documents(user_id):
    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                SELECT id, file_name, pdf_data, created_at
                FROM signed_documents
                WHERE user_id = :user_id
                ORDER BY created_at DESC
            """),
            {"user_id": user_id}
        ).mappings().all()

    documents = []
    for row in rows:
        documents.append({
            "id": row["id"],
            "file_name": row["file_name"],
            "pdf_bytes": base64.b64decode(row["pdf_data"]),
            "created_at": row["created_at"]
        })

    return documents

def delete_signed_document(document_id, user_id):
    with engine.begin() as conn:
        conn.execute(
            text("""
                DELETE FROM signed_documents
                WHERE id = :document_id AND user_id = :user_id
            """),
            {
                "document_id": document_id,
                "user_id": user_id
            }
        )
