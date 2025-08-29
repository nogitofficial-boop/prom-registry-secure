import os
import base64
import hashlib

from fastapi import Request, HTTPException, status
from cryptography.fernet import Fernet, InvalidToken

def _fernet_from_passphrase() -> Fernet:
    passphrase = os.getenv("SECRET_PASSPHRASE")
    if not passphrase:
        raise RuntimeError("SECRET_PASSPHRASE not set. Put it in your .env")
    key = hashlib.sha256(passphrase.encode("utf-8")).digest()
    fkey = base64.urlsafe_b64encode(key)
    return Fernet(fkey)

_FERNET = None
def _get_fernet() -> Fernet:
    global _FERNET
    if _FERNET is None:
        _FERNET = _fernet_from_passphrase()
    return _FERNET

def encrypt_str(s: str) -> str:
    return _get_fernet().encrypt(s.encode("utf-8")).decode("utf-8")

def decrypt_str(s: str) -> str:
    try:
        return _get_fernet().decrypt(s.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return "<DECRYPTION-ERROR>"

def require_admin(request: Request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        token = request.query_params.get("token")
        if token and token == os.getenv("ADMIN_TOKEN"):
            return True
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    token = auth.removeprefix("Bearer ").strip()
    if token != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin token")
    return True

async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "accelerometer=(), camera=(), geolocation=(), gyroscope=(), microphone=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline';"
    return response
