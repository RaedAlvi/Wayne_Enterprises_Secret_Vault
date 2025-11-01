# auth.py
import streamlit as st
from db import fetch_user_by_email, create_user, set_failed_login, insert_audit
from security import password_policy_ok, hash_password, verify_password, new_totp_secret, verify_totp, totp_now, lockout_until_after
from utils import safe_ex

def _init_session():
    for k, v in {
        "user": None,
        "last_active": None,
        "needs_2fa": False
    }.items():
        if k not in st.session_state: st.session_state[k] = v

def register_form():
    st.subheader("Create Account")
    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")
    cpw = st.text_input("Confirm Password", type="password")
    want_2fa = st.checkbox("Enable 2FA (TOTP)?", value=True)

    if st.button("Register"):
        ok, msg = password_policy_ok(pw)
        if not ok:
            st.error(f"Password too weak: {msg}")
            return
        if pw != cpw:
            st.error("Passwords do not match.")
            return
        row = fetch_user_by_email(email)
        if row:
            st.error("Email already registered.")
            return
        secret = new_totp_secret() if want_2fa else None
        hashed = hash_password(pw)
        _, err = safe_ex(create_user, email, hashed, "user", secret)
        if err:
            st.error(err)
            return
        insert_audit(None, "register", email)
        st.success("Account created.")
        if secret:
            st.info("2FA enabled. Use an authenticator app to add this secret:")
            st.code(secret)
            st.caption(f"Current code (demo): {totp_now(secret)}")

def login_form():
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    pw = st.text_input("Password", type="password", key="login_pw")

    if st.button("Login"):
        row = fetch_user_by_email(email)
        if not row:
            st.error("Invalid credentials.")
            return
        uid, uemail, pwhash, role, totp_secret, failed, lockout_until = row
        if lockout_until:
            st.error("Account locked. Try later.")
            return

        if not verify_password(pw, pwhash):
            failed = (failed or 0) + 1
            until = lockout_until_after(failed)
            set_failed_login(email, failed, until)
            insert_audit(uid, "login_fail", f"failed={failed}")
            st.error("Invalid credentials.")
            return

        set_failed_login(email, 0, None)

        if totp_secret:
            st.session_state["needs_2fa"] = True
            st.session_state["user"] = {"id": uid, "email": uemail, "role": role, "totp": totp_secret}
            st.info("Enter your 2FA code to finish login.")
        else:
            st.session_state["user"] = {"id": uid, "email": uemail, "role": role, "totp": None}
            st.session_state["last_active"] = datetime.utcnow().timestamp()
            insert_audit(uid, "login_success", None)
            st.success("Logged in.")

def totp_step():
    if not st.session_state.get("needs_2fa"): return
    st.subheader("Two-Factor Authentication")
    code = st.text_input("Enter 6-digit code", max_chars=6)
    if st.button("Verify 2FA"):
        secret = st.session_state["user"]["totp"]
        if verify_totp(secret, code):
            st.session_state["needs_2fa"] = False
            st.session_state["last_active"] = datetime.utcnow().timestamp()
            insert_audit(st.session_state["user"]["id"], "2fa_success", None)
            st.success("2FA verified.")
        else:
            insert_audit(st.session_state["user"]["id"], "2fa_fail", None)
            st.error("Invalid code.")

def logout_button():
    if st.session_state.get("user"):
        if st.button("Logout"):
            insert_audit(st.session_state["user"]["id"], "logout", None)
            for k in ["user", "last_active", "needs_2fa"]:
                st.session_state[k] = None
            st.success("Logged out.")

def require_auth():
    _init_session()
    if not st.session_state.get("user") or st.session_state.get("needs_2fa"):
        st.warning("Please log in.")
        return False
    return True
