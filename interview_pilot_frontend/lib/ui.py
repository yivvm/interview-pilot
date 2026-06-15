"""Shared UI helpers (global CSS injection)."""

import streamlit as st

_CUSTOM_CSS = """
<style>
/* JD text area: blue border + glow on focus */
div[data-baseweb="textarea"]:focus-within {
    border-color: #095BD9 !important;
    box-shadow: 0 0 0 1px #095BD9 !important;
}

/* Buttons: blue fill, white text */
[data-testid="stButton"] button,
.stButton > button {
    background-color: #095BD9 !important;
    color: #FFFFFF !important;
    border: 1px solid #095BD9 !important;
}
[data-testid="stButton"] button p,
.stButton > button p {
    color: #FFFFFF !important;
} 
[data-testid="stButton"] button:hover,
[data-testid="stButton"] button:active,
[data-testid="stButton"] button:focus,
.stButton > button:hover {
    background-color: #0749AE !important;
    color: #FFFFFF !important;
    border-color: #0749AE !important;
}

/* File uploader "Browse files" button */
[data-testid="stFileUploader"] button {
    background-color: #095BD9 !important;
    color: #FFFFFF !important;
    border: 1px solid #095BD9 !important;
}
[data-testid="stFileUploader"] button:hover,
[data-testid="stFileUploader"] button:active,
[data-testid="stFileUploader"] button:focus {                        
    background-color: #0749AE !important;
    color: #FFFFFF !important;
    border-color: #0749AE !important;
}

/* Slightly larger sidebar text */
section[data-testid="stSidebar"] * { font-size: 1.05rem; }

/* Selected page in the sidebar nav */
section[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #E8F0FB !important;
}

/* Collapse the empty block this style injection creates */
div[data-testid="stElementContainer"]:has(style) { display: none; }
</style>
"""

def inject_css() -> None:
    st.markdown(_CUSTOM_CSS, unsafe_allow_html=True)