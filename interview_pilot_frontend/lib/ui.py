"""Shared UI helpers (global CSS injection)."""

import streamlit as st

from lib.api import upload_resume

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


def resume_input(page_key: str) -> str | None:
    """Show the current resume and let the user upload a new one.
    
    Returns the active session_id (or None if nothing uploaded yet).
    `page_key` keeps each page's uploader state independent.
    """
    current = st.session_state.get("resume_filename")
    if current:
        st.success(f"Using resume: {current}")

    with st.expander("Upload a different resume" if current else "Upload your resume", expanded=not current):
        uploaded = st.file_uploader(
            "Resume (PDF or DOCX)", type=["pdf", "docx"], key=f"{page_key}_uploader"
        )
        if uploaded is not None and st.session_state.get(f"{page_key}_last") != uploaded.name:
            with st.spinner("Uploading and extracting text..."):
                try:
                    result = upload_resume(
                        uploaded.name,
                        uploaded.getvalue(),
                        uploaded.type or "application/octet-stream",
                    )
                except Exception as exc:
                    st.error(f"Upload failed: {exc}")
                else:
                    st.session_state["session_id"] = result["session_id"]
                    st.session_state["resume_filename"] = result["resume_filename"]
                    st.session_state[f"{page_key}_last"] = uploaded.name
                    # New resume -> clear any cache section results in this UI session.
                    for k in ("review_result", "match_result", "interview_result"):
                        st.session_state.pop(k, None)
                    st.rerun()
    
    return st.session_state.get("session_id")

            