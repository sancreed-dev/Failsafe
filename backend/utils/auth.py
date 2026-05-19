import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

try:
    from backend.utils.database import get_connection, init_db
except ModuleNotFoundError:
    from utils.database import get_connection, init_db

SECRET_KEY = os.getenv("FAILSAFE_SECRET_KEY", "failsafe-dev-secret-change-before-deploy")
TOKEN_TTL_MINUTES = int(os.getenv("FAILSAFE_TOKEN_TTL_MINUTES", "480"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

DEMO_EMAIL = "faculty@failsafe.edu"
DEMO_PASSWORD = "failsafe123"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    salt, expected = stored_hash.split("$", 1)
    candidate = hash_password(password, salt).split("$", 1)[1]
    return hmac.compare_digest(candidate, expected)


def seed_demo_user():
    init_db()
    with get_connection() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (DEMO_EMAIL,)).fetchone()
        if existing:
            return
        conn.execute(
            """
            INSERT INTO users (email, name, role, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                DEMO_EMAIL,
                "Faculty Demo",
                "faculty",
                hash_password(DEMO_PASSWORD),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()


def authenticate_user(email: str, password: str):
    seed_demo_user()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
    if not row or not verify_password(password, row["password_hash"]):
        return None
    return {
        "id": row["id"],
        "email": row["email"],
        "name": row["name"],
        "role": row["role"],
    }


def create_access_token(user: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user["email"],
        "name": user["name"],
        "role": user["role"],
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=TOKEN_TTL_MINUTES)).timestamp()),
    }
    signing_input = (
        f"{_b64url(json.dumps(header, separators=(',', ':')).encode())}."
        f"{_b64url(json.dumps(payload, separators=(',', ':')).encode())}"
    )
    signature = hmac.new(SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url(signature)}"


def decode_token(token: str) -> dict:
    try:
        header_part, payload_part, signature_part = token.split(".")
        signing_input = f"{header_part}.{payload_part}"
        expected = _b64url(
            hmac.new(SECRET_KEY.encode(), signing_input.encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(signature_part, expected):
            raise ValueError("Invalid signature")
        payload = json.loads(_b64url_decode(payload_part))
        if int(payload["exp"]) < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError("Token expired")
        return payload
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    return {
        "email": payload["sub"],
        "name": payload["name"],
        "role": payload["role"],
    }
