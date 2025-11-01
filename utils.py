"""
Utility functions: CSS loading, formatting, error handling
"""
import streamlit as st
from typing import Any, Callable

def safe_exec(func: Callable, *args, **kwargs) -> Any:
    """Safely execute function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"

def load_css():
    """Load custom Wayne Enterprises CSS"""
    st.markdown("""
        <style>
        /* Wayne Enterprises Dark Theme */
        :root {
            --wayne-dark: #0a0e1a;
            --wayne-navy: #1a1d2e;
            --wayne-gold: #d4af37;
            --wayne-gold-light: #f4e4a6;
            --wayne-blue: #00ff9f;
            --wayne-red: #ff6b9d;
        }
        
        /* Main container */
        .stApp {
            background: linear-gradient(135deg, #0a0e1a 0%, #1a1d2e 100%);
            color: #e2e8f0;
        }
        
        /* Header */
        .vault-header {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(26, 29, 46, 0.8), rgba(10, 14, 26, 0.9));
            border: 2px solid var(--wayne-gold);
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 0 30px rgba(212, 175, 55, 0.3);
        }
        
        .vault-header h1 {
            color: var(--wayne-gold);
            font-size: 2.5rem;
            font-weight: 900;
            letter-spacing: 3px;
            text-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
            margin: 0;
        }
        
        .vault-subtitle {
            color: var(--wayne-gold-light);
            font-size: 1rem;
            letter-spacing: 2px;
            margin-top: 0.5rem;
        }
        
        .security-badge {
            display: inline-block;
            background: rgba(0, 255, 159, 0.1);
            border: 1px solid var(--wayne-blue);
            color: var(--wayne-blue);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            margin-top: 1rem;
            font-size: 0.9rem;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        /* Auth container */
        .auth-container {
            background: rgba(26, 29, 46, 0.6);
            border: 1px solid var(--wayne-gold);
            border-radius: 15px;
            padding: 2rem;
            backdrop-filter: blur(10px);
        }
        
        /* Security info box */
        .security-info {
            background: rgba(0, 255, 159, 0.05);
            border-left: 4px solid var(--wayne-blue);
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 5px;
        }
        
        .security-info h4 {
            color: var(--wayne-blue);
            margin-top: 0;
        }
        
        .security-info ul {
            color: #cbd5e0;
            margin: 0.5rem 0;
        }
        
        /* User profile */
        .user-profile {
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.1), rgba(26, 29, 46, 0.8));
            border: 1px solid var(--wayne-gold);
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .user-profile h3 {
            color: var(--wayne-gold);
            margin: 0;
            font-size: 1.2rem;
        }
        
        .role-badge {
            background: rgba(0, 255, 159, 0.2);
            color: var(--wayne-blue);
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            display: inline-block;
            margin-top: 0.5rem;
        }
        
        /* Metric cards */
        .metric-card {
            background: rgba(26, 29, 46, 0.8);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        
        .metric-card.income {
            border-color: var(--wayne-blue);
            background: linear-gradient(135deg, rgba(0, 255, 159, 0.1), rgba(26, 29, 46, 0.9));
        }
        
        .metric-card.expense {
            border-color: var(--wayne-red);
            background: linear-gradient(135deg, rgba(255, 107, 157, 0.1), rgba(26, 29, 46, 0.9));
        }
        
        .metric-card h4 {
            color: #a0aec0;
            font-size: 0.9rem;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .metric-card h2 {
            color: var(--wayne-gold);
            font-size: 2rem;
            margin: 0.5rem 0 0 0;
            font-weight: 900;
        }
        
        /* Transaction card */
        .transaction-card {
            background: rgba(26, 29, 46, 0.6);
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 4px solid var(--wayne-gold);
            transition: all 0.3s ease;
        }
        
        .transaction-card:hover {
            background: rgba(26, 29, 46, 0.8);
            transform: translateX(5px);
            box-shadow: 0 5px 20px rgba(212, 175, 55, 0.2);
        }
        
        /* Buttons */
        .stButton button {
            background: linear-gradient(135deg, var(--wayne-gold), #b8941f);
            color: var(--wayne-dark);
            font-weight: 700;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stButton button:hover {
            background: linear-gradient(135deg, #b8941f, var(--wayne-gold));
            box-shadow: 0 5px 20px rgba(212, 175, 55, 0.4);
            transform: translateY(-2px);
        }
        
        /* Forms */
        .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {
            background: rgba(26, 29, 46, 0.8) !important;
            border: 1px solid var(--wayne-gold) !important;
            color: #e2e8f0 !important;
            border-radius: 8px !important;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: var(--wayne-blue) !important;
            box-shadow: 0 0 10px rgba(0, 255, 159, 0.3) !important;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            background: rgba(26, 29, 46, 0.4);
            border-radius: 10px;
            padding: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            color: #a0aec0;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background: var(--wayne-gold) !important;
            color: var(--wayne-dark) !important;
            border-radius: 8px;
        }
        
        /* Dataframe */
        .stDataFrame {
            background: rgba(26, 29, 46, 0.6);
            border-radius: 10px;
        }
        
        /* Success/Error messages */
        .stSuccess {
            background: rgba(0, 255, 159, 0.1);
            border-left: 4px solid var(--wayne-blue);
        }
        
        .stError {
            background: rgba(255, 107, 157, 0.1);
            border-left: 4px solid var(--wayne-red);
        }
        
        .stWarning {
            background: rgba(212, 175, 55, 0.1);
            border-left: 4px solid var(--wayne-gold);
        }
        
        .stInfo {
            background: rgba(100, 150, 255, 0.1);
            border-left: 4px solid #6496ff;
        }
        </style>
    """, unsafe_allow_html=True)
