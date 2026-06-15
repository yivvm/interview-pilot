"""InterviewPilot - Streamlit frontend entry point

Run with:
    streamlit run streamlit_app.py
Opens at http://localhost:8501
"""

import streamlit as st

from lib.ui import inject_css

inject_css()

st.set_page_config(page_title="InterviewPilot", layout="wide")

st.title("Interview Pilot")
st.write("AI-powered resume review and interview prep - all running locally.")
st.info("Navigate with the siderbar: **Upload → Resume Review → Job Description Match → Interview Prep**.")

# Sidebar always show where the user is in the flow.
with st.sidebar:
    st.header("Session")
    session_id = st.session_state.get("session_id")
    resume_name = st.session_state.get("resume_filename")
    st.write(f"**Session ID:** {session_id or '- none yet -'}")
    st.write(f"**Resume:** {resume_name or '- none uploaded -'}")

