"""Authentication and Access Control Service for SPECTRAMARK."""

import hashlib
import hmac
import time
from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Header, status

router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_AUTH_KEY = b"SPECTRAMARK-SECURE-TOKEN-SECRET-SALT-v1"

# Default administrative user credentials
USERS = {
    "admin": {
        "username": "admin",
        # SHA256 of 'spectramark2026'
        "password_hash": hashlib.sha256("spectramark2026".encode("utf-8")).hexdigest(),
        "full_name": "Lead Forensic Examiner",
        "role": "Chief Forensic Analyst",
        "organization": "SPECTRAMARK Security Labs",
    },
    "investigator": {
        "username": "investigator",
        "password_hash": hashlib.sha256("forensic123".encode("utf-8")).hexdigest(),
        "full_name": "Digital Forensics Investigator",
        "role": "Forensic Auditor",
        "organization": "Cyber Crime Division",
    }
}


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: Dict[str, Any]
    expires_in: int


def create_token(username: str) -> str:
    """Creates an HMAC-signed authentication token with timestamp."""
    timestamp = int(time.time())
    payload = f"{username}:{timestamp}"
    signature = hmac.new(SECRET_AUTH_KEY, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}:{signature}"


def verify_token(token: str) -> Optional[str]:
    """Validates an HMAC-signed authentication token."""
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None
        username, timestamp_str, signature = parts
        payload = f"{username}:{timestamp_str}"
        expected_sig = hmac.new(SECRET_AUTH_KEY, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        return username
    except Exception:
        return None


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    """Authenticates users and provides session tokens."""
    username = req.username.strip().lower()
    user = USERS.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Use 'admin' / 'spectramark2026'.",
        )

    pwd_hash = hashlib.sha256(req.password.strip().encode("utf-8")).hexdigest()
    if not hmac.compare_digest(pwd_hash, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password. Default demo password is 'spectramark2026'.",
        )

    token = create_token(username)
    return LoginResponse(
        token=token,
        user={
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"],
            "organization": user["organization"],
        },
        expires_in=86400,
    )


@router.get("/me")
async def get_current_user(authorization: Optional[str] = Header(None)):
    """Validates token and returns current user details."""
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")

    token = authorization.replace("Bearer ", "").strip()
    username = verify_token(token)
    if not username or username not in USERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session token")

    user = USERS[username]
    return {
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "organization": user["organization"],
    }

