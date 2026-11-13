from auth_view import render_auth_page
from dashboard import render_main_app
import streamlit as st

st.set_page_config(
    page_title="AquaTrack Pro | Hydration Analytics",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(90deg, #0066cc 0%, #00b4d8 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    </style>
""",
    unsafe_allow_html=True,
)

if "user" not in st.session_state:
  st.session_state.user = None

if not st.session_state.user:
  render_auth_page()
else:
  render_main_app(st.session_state.user["username"])