# app.py
import time
import pandas as pd
import streamlit as st
from datetime import datetime
from db import init_db, add_transaction, list_transactions, insert_audit, list_audit
from auth import register_form, login_form, totp_step, logout_button, require_auth
from security import encrypt_note, decrypt_note, session_stale
from utils import safe_ex

st.set_page_config(page_title="Wayne Enterprises Secret Vault", page_icon="💰")
init_db()

def _touch_session():
    if st.session_state.get("last_active") and session_stale(st.session_state["last_active"]):
        uid = st.session_state["user"]["id"] if st.session_state.get("user") else None
        insert_audit(uid, "session_timeout", None)
        for k in ["user", "last_active", "needs_2fa"]:
            st.session_state[k] = None
        st.warning("Session expired due to inactivity. Please log in again.")
    else:
        if st.session_state.get("user"):
            st.session_state["last_active"] = time.time()

page = st.sidebar.selectbox("Menu", ["Home", "Register", "Login / 2FA", "Dashboard", "Profile", "Admin Logs"])

if page == "Home":
    st.title("Wayne Enterprises Secret Vault")
    st.write("Secure login, encrypted storage, session controls, audit logs.")

elif page == "Register":
    register_form()

elif page == "Login / 2FA":
    login_form()
    totp_step()

elif page == "Dashboard":
    _touch_session()
    if not require_auth(): st.stop()
    st.header("Add Transaction")
    ttype = st.selectbox("Type", ["income","expense"])
    amt = st.text_input("Amount (number)", value="0")
    cat = st.text_input("Category (e.g., salary, food)")
    note = st.text_area("Note (will be encrypted)")
    
    # Validation: numeric amounts only, length limits, basic sanitation
    if st.button("Save"):
        try:
            amount = float(amt)
            if amount <= 0: raise ValueError("Amount must be > 0")
            if len(cat) > 50: raise ValueError("Category too long")
            if len(note) > 500: raise ValueError("Note too long")
            enc = encrypt_note(note or "")
            add_transaction(st.session_state["user"]["id"], ttype, amount, cat.strip(), enc)
            insert_audit(st.session_state["user"]["id"], "add_transaction", f"{ttype}:{amount}:{cat}")
            st.success("Saved.")
        except ValueError as ve:
            st.error(f"Validation error: {ve}")
        except Exception:
            st.error("Could not save. Please try again.")
            
    st.subheader("Your Recent Transactions")
    rows = list_transactions(st.session_state["user"]["id"], limit=100)
    if rows:
        view = []
        for rid, ttype, amount, category, note_enc, created in rows:
            dec = ""
            try:
                dec = decrypt_note(note_enc) if note_enc else ""
            except Exception:
                dec = "[unreadable]"
            view.append({"id": rid, "type": ttype, "amount": amount, "category": category, "note": dec, "created": created})
        st.dataframe(pd.DataFrame(view))

    logout_button()

elif page == "Profile":
    _touch_session()
    if not require_auth(): st.stop()
    st.header("Profile")
    email = st.session_state["user"]["email"]
    st.write(f"Email: **{email}**")
    st.caption("Future: add editable profile fields with validation.")
    logout_button()

elif page == "Admin Logs":
    _touch_session()
    if not st.session_state.get("user") or st.session_state["user"]["role"] != "admin":
        st.error("Admins only.")
        st.stop()
    st.header("Audit Logs")
    st.dataframe(pd.DataFrame(list_audit(200), columns=["id","user_id","action","meta","created_at"]))
    logout_button()
