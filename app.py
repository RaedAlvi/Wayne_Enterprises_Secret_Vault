"""
Wayne Enterprises Secret Vault - Main Application
Secure financial vault with military-grade encryption
"""
import streamlit as st
from datetime import datetime, timedelta
import time
from auth import register_form, login_form, totp_step, logout_button, require_auth
from db import init_db, get_transactions, add_transaction, get_audit_logs, log_audit
from security import encrypt_note, decrypt_note
from utils import load_css, safe_exec, format_currency
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Wayne Enterprises Secret Vault",
    page_icon="🦇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Load custom CSS
load_css()

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'totp_verified' not in st.session_state:
    st.session_state.totp_verified = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'last_activity' not in st.session_state:
    st.session_state.last_activity = datetime.now()
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'user'

# Session timeout check (15 minutes)
def check_session_timeout():
    if st.session_state.authenticated:
        time_diff = datetime.now() - st.session_state.last_activity
        if time_diff > timedelta(minutes=15):
            st.session_state.authenticated = False
            st.session_state.totp_verified = False
            st.session_state.user_email = None
            st.warning("⏰ Session expired due to inactivity. Please login again.")
            st.rerun()
        else:
            st.session_state.last_activity = datetime.now()

check_session_timeout()

# Header with Wayne Enterprises branding
def render_header():
    st.markdown("""
        <div class="vault-header">
            <h1>🦇 WAYNE ENTERPRISES</h1>
            <p class="vault-subtitle">CLASSIFIED FINANCIAL VAULT</p>
            <div class="security-badge">🔒 MILITARY-GRADE ENCRYPTION ACTIVE</div>
        </div>
    """, unsafe_allow_html=True)

render_header()

# Main application logic
if not st.session_state.authenticated:
    # Authentication page
    tab1, tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
    
    with tab1:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        login_form()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        register_form()
        st.markdown('</div>', unsafe_allow_html=True)

elif not st.session_state.totp_verified:
    # 2FA verification page
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    totp_step()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Main dashboard (authenticated and 2FA verified)
    require_auth()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
            <div class="user-profile">
                <h3>👤 {st.session_state.user_email}</h3>
                <p class="role-badge">{st.session_state.user_role.upper()}</p>
            </div>
        """, unsafe_allow_html=True)
        
        logout_button()
        
        st.markdown("---")
        st.markdown("### 🛡️ Security Status")
        st.success("✅ 2FA Enabled")
        st.success("✅ AES-256 Encryption")
        st.success("✅ Session Active")
        
        # Session timeout warning
        time_remaining = 15 - (datetime.now() - st.session_state.last_activity).seconds // 60
        if time_remaining <= 5:
            st.warning(f"⏰ Session expires in {time_remaining} minutes")
    
    # Main content
    st.markdown("## 💼 Financial Dashboard")
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["💰 Transactions", "➕ Add Transaction", "📊 Audit Logs"])
    
    with tab1:
        st.markdown("### Transaction History")
        
        transactions = get_transactions(st.session_state.user_email)
        
        if transactions:
            # Summary cards
            col1, col2, col3 = st.columns(3)
            
            total_income = sum(t[3] for t in transactions if t[2] == 'income')
            total_expense = sum(t[3] for t in transactions if t[2] == 'expense')
            net_balance = total_income - total_expense
            
            with col1:
                st.markdown(f"""
                    <div class="metric-card income">
                        <h4>Total Income</h4>
                        <h2>{format_currency(total_income)}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="metric-card expense">
                        <h4>Total Expenses</h4>
                        <h2>{format_currency(total_expense)}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                balance_class = "income" if net_balance >= 0 else "expense"
                st.markdown(f"""
                    <div class="metric-card {balance_class}">
                        <h4>Net Balance</h4>
                        <h2>{format_currency(net_balance)}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Transaction table
            for txn in transactions:
                txn_id, user_email, txn_type, amount, category, note_encrypted, timestamp = txn
                
                # Decrypt note
                note = decrypt_note(note_encrypted) if note_encrypted else "No note"
                
                icon = "📈" if txn_type == "income" else "📉"
                color = "#00ff9f" if txn_type == "income" else "#ff6b9d"
                
                st.markdown(f"""
                    <div class="transaction-card" style="border-left: 4px solid {color};">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4>{icon} {category.upper()}</h4>
                                <p style="color: #a0aec0; font-size: 0.9rem;">{timestamp}</p>
                                <p style="margin-top: 8px;">🔒 {note}</p>
                            </div>
                            <div style="text-align: right;">
                                <h3 style="color: {color};">{format_currency(amount)}</h3>
                                <p style="color: #a0aec0; font-size: 0.85rem;">{txn_type.upper()}</p>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 No transactions yet. Add your first transaction!")
    
    with tab2:
        st.markdown("### Add New Transaction")
        
        with st.form("add_transaction_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                txn_type = st.selectbox("Type", ["income", "expense"], 
                                       format_func=lambda x: "📈 Income" if x == "income" else "📉 Expense")
                amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, format="%.2f")
            
            with col2:
                category = st.text_input("Category", max_chars=50, 
                                        placeholder="e.g., Salary, Investment, Equipment")
                
            note = st.text_area("Encrypted Note (Optional)", max_chars=1000,
                               placeholder="Add a secure note (will be encrypted with AES-256)")
            
            submitted = st.form_submit_button("🔐 Add Encrypted Transaction", use_container_width=True)
            
            if submitted:
                if not category or len(category.strip()) == 0:
                    st.error("❌ Category is required")
                elif amount <= 0:
                    st.error("❌ Amount must be greater than 0")
                else:
                    # Encrypt note
                    note_encrypted = encrypt_note(note) if note else None
                    
                    # Add transaction
                    success = add_transaction(
                        st.session_state.user_email,
                        txn_type,
                        amount,
                        category.strip(),
                        note_encrypted
                    )
                    
                    if success:
                        st.success(f"✅ Transaction added successfully! Amount: {format_currency(amount)}")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to add transaction")
    
    with tab3:
        st.markdown("### 📊 Audit Logs")
        
        if st.session_state.user_role == 'admin':
            st.info("🔍 Viewing all system audit logs (Admin access)")
            logs = get_audit_logs(admin=True)
        else:
            st.info("🔍 Viewing your account activity")
            logs = get_audit_logs(user_email=st.session_state.user_email)
        
        if logs:
            df = pd.DataFrame(logs, columns=['ID', 'User', 'Action', 'IP Address', 'Timestamp'])
            df = df.drop('ID', axis=1)
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                action_filter = st.multiselect("Filter by Action", 
                                              options=df['Action'].unique(),
                                              default=df['Action'].unique())
            
            filtered_df = df[df['Action'].isin(action_filter)]
            
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            
            # Export option
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Export Audit Logs (CSV)",
                data=csv,
                file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("📭 No audit logs available")
        
        # Display security metrics
        if logs:
            st.markdown("---")
            st.markdown("### 🛡️ Security Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            login_attempts = sum(1 for log in logs if 'login' in log[2].lower())
            failed_logins = sum(1 for log in logs if 'failed' in log[2].lower())
            total_actions = len(logs)
            
            with col1:
                st.metric("Total Actions", total_actions)
            with col2:
                st.metric("Login Attempts", login_attempts)
            with col3:
                st.metric("Failed Attempts", failed_logins, 
                         delta="Alert" if failed_logins > 5 else None,
                         delta_color="inverse")
