# security.py
import os, re, bcrypt, pyotp, time
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
FERNET_KEY = os.getenv("FERNET_KEY", "").encode()
SESSION_IDLE_SECONDS = int(os.getenv("SESSION_IDLE_SECONDS", "300") or "300")
fernet = Fernet(FERNET_KEY) if FERNET_KEY else None

def password_policy_ok(pw: str) -> (bool, str):
    if len(pw) < 8: return False, "Minimum length 8."
    if not re.search(r"[A-Z]", pw): return False, "Add an uppercase letter."
    if not re.search(r"[a-z]", pw): return False, "Add a lowercase letter."
    if not re.search(r"\d", pw): return False, "Add a digit."
    if not re.search(r"[^\w\s]", pw): return False, "Add a symbol."
    return True, ""

def hash_password(pw: str) -> bytes:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

def verify_password(pw: str, hashed: bytes) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed)
    except Exception:
        return False

def encrypt_note(text: str) -> bytes:
    if not fernet: raise RuntimeError("FERNET_KEY not configured")
    return fernet.encrypt(text.encode())

def decrypt_note(blob: bytes) -> str:
    if not fernet: raise RuntimeError("FERNET_KEY not configured")
    return fernet.decrypt(blob).decode()

def new_totp_secret():
    return pyotp.random_base32()

def totp_now(secret: str) -> str:
    return pyotp.TOTP(secret).now()

def verify_totp(secret: str, code: str) -> bool:
    try:
        return pyotp.TOTP(secret).verify(code, valid_window=1)
    except Exception:
        return False

def session_stale(last_active_ts: float) -> bool:
    return (time.time() - last_active_ts) > SESSION_IDLE_SECONDS

def lockout_until_after(failed_count: int):
    if failed_count >= 5:
        return (datetime.utcnow() + timedelta(minutes=5)).isoformat(sep=" ", timespec="seconds")
    return None
