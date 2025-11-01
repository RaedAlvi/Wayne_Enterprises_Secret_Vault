"""
Security module: Password hashing, TOTP, and encryption
"""
import hashlib
import secrets
import re
from cryptography.fernet import Fernet
import pyotp
import qrcode
from io import BytesIO
import base64
import os

# Load encryption key from environment
FERNET_KEY = os.getenv('FERNET_KEY')
if not FERNET_KEY:
    # Generate a key if not exists (for demo purposes)
    FERNET_KEY = Fernet.generate_key().decode()
    print(f"⚠️ WARNING: Using generated FERNET_KEY: {FERNET_KEY}")
    print("⚠️ Set this as environment variable for production!")

cipher = Fernet(FERNET_KEY.encode() if isinstance(FERNET_KEY, str) else FERNET_KEY)

# Password Policy
def password_policy_ok(password: str) -> tuple[bool, str]:
    """
    Enforce strong password policy:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*)"
    
    return True, "Password meets requirements"

# Password Hashing (bcrypt-style with SHA-256)
def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, pwd_hash = stored_hash.split('$')
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == pwd_hash
    except:
        return False

# TOTP (Time-based One-Time Password)
def new_totp_secret() -> str:
    """Generate a new TOTP secret"""
    return pyotp.random_base32()

def verify_totp(secret: str, token: str) -> bool:
    """Verify TOTP token"""
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    except:
        return False

def totp_qr_code(secret: str, email: str) -> bytes:
    """Generate QR code for TOTP setup"""
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=email, issuer_name="Wayne Enterprises Vault")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer.getvalue()

# AES-256 Encryption for Notes
def encrypt_note(plaintext: str) -> str:
    """Encrypt note using AES-256 (Fernet)"""
    if not plaintext:
        return ""
    
    try:
        encrypted = cipher.encrypt(plaintext.encode())
        return encrypted.decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return ""

def decrypt_note(ciphertext: str) -> str:
    """Decrypt note using AES-256 (Fernet)"""
    if not ciphertext:
        return ""
    
    try:
        decrypted = cipher.decrypt(ciphertext.encode())
        return decrypted.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return "[Decryption failed]"
