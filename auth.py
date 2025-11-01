"""
Authentication module with password policy, 2FA, and account lockout
"""
import streamlit as st
from datetime import datetime, timedelta
import time
from security import (
    password_policy_ok, 
    hash_password, 
    verify_password, 
    new_totp_secret, 
    verify_totp, 
    totp_qr_code
)
from db import (
    user_exists, 
    create_user, 
    get_user, 
    update_failed_attempts, 
    reset_failed_attempts,
    is_account_locked,
    log_audit
)
from utils import safe_exec

def register_form():
    """User registration with strong password policy"""
    st.markdown("### 🔐 Create Secure Account")
    st.markdown("""
        <div class="security-info">
            <h4>🛡️ Security Requirements:</h4>
            <ul>
                <li>✓ Minimum 8 characters</li>
                <li>✓ At least one uppercase letter</li>
                <li>✓ At least one lowercase letter</li>
                <li>✓ At least one number</li>
                <li>✓ At least one special character (!@#$%^&*)</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("register_form"):
        email = st.text_input("Email", placeholder="bruce.wayne@wayneenterprises.com")
        password = st.text_input("Password", type="password", 
                                placeholder="Create a strong password")
        password_confirm = st.text_input("Confirm Password", type="password",
                                        placeholder="Re-enter your password")
        
        role = st.selectbox("Role", ["user", "admin"], 
                           help="Admin role grants access to all audit logs")
        
        submitted = st.form_submit_button("🦇 Register Account", use_container_width=True)
        
        if submitted:
            # Validation
            if not email or '@' not in email:
                st.error("❌ Please enter a valid email address")
                return
            
            if password != password_confirm:
                st.error("❌ Passwords do not match")
                return
            
            # Check password policy
            policy_ok, message = password_policy_ok(password)
            if not policy_ok:
                st.error(f"❌ {message}")
                return
            
            # Check if user exists
            if user_exists(email):
                st.error("❌ Email already registered")
                return
            
            # Generate TOTP secret
            totp_secret = new_totp_secret()
            
            # Hash password
            password_hash = hash_password(password)
            
            # Create user
            success = create_user(email, password_hash, totp_secret, role)
            
            if success:
                log_audit(email, "User registered", "0.0.0.0")
                
                st.success("✅ Account created successfully!")
                st.info("📱 Please save your 2FA secret key for authentication")
                
                # Display TOTP QR code
                st.markdown("### 📲 Set Up Two-Factor Authentication")
                st.markdown("""
                    Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
                """)
                
                qr_img = totp_qr_code(totp_secret, email)
                st.image(qr_img, width=300)
                
                st.code(totp_secret, language=None)
                st.warning("⚠️ Save this secret key securely. You'll need it to login.")
                
                time.sleep(20)
                st.rerun()
            else:
                st.error("❌ Registration failed. Please try again.")

def login_form():
    """Login form with account lockout protection"""
    st.markdown("### 🔐 Secure Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="bruce.wayne@wayneenterprises.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        submitted = st.form_submit_button("🔓 Login", use_container_width=True)
        
        if submitted:
            if not email or not password:
                st.error("❌ Please enter both email and password")
                return
            
            # Check if account is locked
            if is_account_locked(email):
                st.error("🔒 Account locked due to multiple failed login attempts. Please try again in 15 minutes.")
                log_audit(email, "Login attempt - account locked", "0.0.0.0")
                return
            
            # Get user
            user = get_user(email)
            
            if not user:
                log_audit(email, "Login failed - user not found", "0.0.0.0")
                st.error("❌ Invalid credentials")
                return
            
            user_id, stored_email, password_hash, totp_secret, failed_attempts, lockout_until, role = user
            
            # Verify password
            if not verify_password(password, password_hash):
                # Increment failed attempts
                new_attempts = failed_attempts + 1
                update_failed_attempts(email, new_attempts)
                
                remaining = 5 - new_attempts
                if remaining > 0:
                    st.error(f"❌ Invalid credentials. {remaining} attempts remaining.")
                else:
                    st.error("🔒 Account locked for 15 minutes due to too many failed attempts.")
                
                log_audit(email, f"Login failed - incorrect password (attempt {new_attempts})", "0.0.0.0")
                return
            
            # Reset failed attempts on successful password verification
            reset_failed_attempts(email)
            
            # Set session state
            st.session_state.authenticated = True
            st.session_state.user_email = email
            st.session_state.totp_secret = totp_secret
            st.session_state.user_role = role
            st.session_state.last_activity = datetime.now()
            
            log_audit(email, "Password verified - awaiting 2FA", "0.0.0.0")
            
            st.success("✅ Password verified! Please enter your 2FA code.")
            time.sleep(1)
            st.rerun()

def totp_step():
    """Two-factor authentication step"""
    st.markdown("### 🔐 Two-Factor Authentication")
    st.info(f"📧 Logged in as: **{st.session_state.user_email}**")
    
    st.markdown("""
        <div class="security-info">
            <p>🛡️ Enter the 6-digit code from your authenticator app</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("totp_form"):
        totp_code = st.text_input("6-Digit Code", max_chars=6, placeholder="000000")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("✅ Verify", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.totp_secret = None
            st.rerun()
        
        if submitted:
            if not totp_code or len(totp_code) != 6:
                st.error("❌ Please enter a 6-digit code")
                return
            
            if verify_totp(st.session_state.totp_secret, totp_code):
                st.session_state.totp_verified = True
                log_audit(st.session_state.user_email, "2FA verified - login successful", "0.0.0.0")
                st.success("✅ Authentication successful!")
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                log_audit(st.session_state.user_email, "2FA verification failed", "0.0.0.0")
                st.error("❌ Invalid 2FA code. Please try again.")

def logout_button():
    """Logout button"""
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        email = st.session_state.user_email
        log_audit(email, "User logged out", "0.0.0.0")
        
        st.session_state.authenticated = False
        st.session_state.totp_verified = False
        st.session_state.user_email = None
        st.session_state.totp_secret = None
        st.session_state.user_role = 'user'
        st.success("✅ Logged out successfully")
        time.sleep(1)
        st.rerun()

def require_auth():
    """Decorator to require authentication"""
    if not st.session_state.authenticated or not st.session_state.totp_verified:
        st.error("❌ Unauthorized access. Please login.")
        st.stop()
