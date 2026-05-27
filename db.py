import os
import bcrypt
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

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
