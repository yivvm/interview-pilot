"""InterviewPilot - Streamlit frontend entry point

Run with:
    streamlit run streamlit_app.py
Opens at http://localhost:8501
"""

from pathlib import Path

import streamlit as st

from lib.ui import inject_css

st.set_page_config(page_title="InterviewPilot", layout="wide")

inject_css()

DOCS = Path(__file__).resolve().parent.parent / "docs"   # repo-root /docs

st.title("Interview Pilot")
st.write("AI-powered resume review and interview prep - all running locally.")

# Overview slides (rendered from docs/)
for _slide in ("user-journey.png", "features.png", "trust.png"):
    _img = DOCS / _slide
    if _img.exists():
        st.image(str(_img), use_column_width=True)

# Sidebar always show where the user is in the flow.
with st.sidebar:
    st.header("Session")
    session_id = st.session_state.get("session_id")
    resume_name = st.session_state.get("resume_filename")
    st.write(f"**Session ID:** {session_id or '- none yet -'}")
    st.write(f"**Resume:** {resume_name or '- none uploaded -'}")

