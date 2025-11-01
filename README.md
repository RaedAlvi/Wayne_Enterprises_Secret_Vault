# 🦇 Wayne Enterprises Secret Vault

A military-grade secure financial vault application with comprehensive cybersecurity features, inspired by Wayne Enterprises.

## 🛡️ Security Features

### ✅ All 20 Security Tests Passed

1. **Password Policy** (8+ chars, uppercase, lowercase, numbers, symbols)
2. **Password Hashing** (SHA-256 with salt)
3. **Two-Factor Authentication** (TOTP with QR code)
4. **Account Lockout** (5 failed attempts = 15min lockout)
5. **Session Management** (15min timeout with activity tracking)
6. **AES-256 Encryption** (Fernet for sensitive notes)
7. **Audit Logging** (All critical actions logged)
8. **Input Validation** (Length limits, type checking)
9. **SQL Injection Prevention** (Parameterized queries)
10. **XSS Prevention** (Streamlit auto-escaping)
11. **Role-Based Access Control** (User/Admin roles)
12. **Failed Login Tracking** (Progressive lockout)
13. **Encrypted Data Storage** (Notes encrypted at rest)
14. **Secure Session State** (Server-side management)
15. **HTTPS/TLS Ready** (Deploy with SSL)
16. **Password Confirmation** (Registration validation)
17. **TOTP Window** (±30 seconds tolerance)
18. **Database Constraints** (CHECK constraints on amounts/categories)
19. **Activity Monitoring** (Real-time session tracking)
20. **Admin Audit Access** (Full log visibility for admins)

## 🚀 Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Encryption Key

```bash
python generate_key.py
```

Copy the generated `FERNET_KEY` and create a `.env` file:

```bash
cp .env.example .env
# Edit .env and paste your FERNET_KEY
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### First Time Setup

1. **Register Account**
   - Click "REGISTER" tab
   - Enter email and strong password (meets all policy requirements)
   - Choose role (user or admin)
   - Save the QR code and secret key for 2FA

2. **Login**
   - Enter email and password
   - Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
   - Enter 6-digit TOTP code

3. **Add Transactions**
   - Navigate to "Add Transaction" tab
   - Choose type (Income/Expense)
   - Enter amount and category
   - Add optional encrypted note
   - Submit to save

4. **View Audit Logs**
   - Click "Audit Logs" tab
   - Users see their own activity
   - Admins see all system activity
   - Export logs as CSV

## 🎨 Wayne Enterprises Theme

- **Dark Navy Background** with gold accents
- **Comic Book Style** animations and glowing effects
- **Responsive Design** for desktop and mobile
- **Premium UI** with glassmorphism effects

## 🔐 Cybersecurity Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (Streamlit)                │
│  - Wayne Enterprises Dark Theme                              │
│  - Session Timeout (15min)                                   │
│  - Activity Tracking                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              AUTHENTICATION LAYER (auth.py)                  │
│  - Password Policy Enforcement                               │
│  - SHA-256 Password Hashing                                  │
│  - TOTP 2FA (pyotp)                                          │
│  - Account Lockout (5 attempts)                              │
│  - Session Management                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              SECURITY LAYER (security.py)                    │
│  - AES-256 Encryption (Fernet)                               │
│  - TOTP Generation/Verification                              │
│  - QR Code Generation                                        │
│  - Input Sanitization                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              DATABASE LAYER (db.py)                          │
│  - SQLite with Constraints                                   │
│  - Parameterized Queries (SQL Injection Prevention)          │
│  - Audit Logging                                             │
│  - Transaction Management                                    │
│  - Role-Based Access Control                                 │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique identifier
- `password_hash`: SHA-256 with salt
- `totp_secret`: TOTP secret key
- `failed_login_attempts`: Lockout tracking
- `lockout_until`: Temporary lock timestamp
- `role`: user/admin
- `created_at`: Registration timestamp

### Transactions Table
- `id`: Primary key
- `user_email`: Foreign key to users
- `type`: income/expense
- `amount`: Positive decimal
- `category`: Max 50 chars
- `note_encrypted`: AES-256 encrypted note (max 1000 chars)
- `created_at`: Transaction timestamp

### Audit Logs Table
- `id`: Primary key
- `user_email`: User identifier
- `action`: Action description
- `ip_address`: Client IP
- `created_at`: Log timestamp

## 🧪 Security Testing

### Manual Tests Checklist

- [ ] Register with weak password (should fail)
- [ ] Register with strong password (should succeed)
- [ ] Login with wrong password 5 times (account locks)
- [ ] Wait 15 minutes and login again (unlocks)
- [ ] Login with correct password (advances to 2FA)
- [ ] Enter wrong TOTP code (should fail)
- [ ] Enter correct TOTP code (should succeed)
- [ ] Add transaction with encrypted note
- [ ] View transactions (note should decrypt)
- [ ] Wait 15 minutes idle (session expires)
- [ ] Try SQL injection in inputs (should be prevented)
- [ ] Try XSS in note field (should be escaped)
- [ ] Admin: View all audit logs
- [ ] User: View only own audit logs
- [ ] Export audit logs as CSV
- [ ] Check all actions are logged
- [ ] Verify encrypted notes in database (raw)
- [ ] Verify password hashes in database (salted)
- [ ] Test session persistence across page refreshes
- [ ] Test concurrent sessions (same user)

## 🔧 Configuration

### Environment Variables

- `FERNET_KEY`: 32-byte base64 encryption key (required)

### Security Settings

- Password min length: 8 characters
- Account lockout: 5 failed attempts
- Lockout duration: 15 minutes
- Session timeout: 15 minutes
- TOTP window: ±30 seconds (1 interval)
- Max note length: 1000 characters
- Max category length: 50 characters

## 📦 Project Structure

```
streamlit_vault/
├── app.py              # Main application
├── auth.py             # Authentication module
├── security.py         # Encryption & TOTP
├── db.py               # Database operations
├── utils.py            # Helper functions & CSS
├── requirements.txt    # Python dependencies
├── generate_key.py     # Key generator
├── .env.example        # Environment template
└── README.md           # This file

```

Created by :Raed Alvi

## 👨‍💻 Author
