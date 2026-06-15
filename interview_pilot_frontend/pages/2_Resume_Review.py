import streamlit as st

from lib.api import review_resume_session
from lib.ui import inject_css

inject_css()

st.title("2 · Resume Review")

session_id = st.session_state.get("session_id")
if not session_id:
    st.warning("Please upload a resume first on the **1 · Upload** page.")
    st.stop()

st.write(f"Reviewing resume: **{st.session_state.get('resume_filename', '')}**")

if st.button("Analyze my resume"):
    with st.spinner("Analyzing... (first run can take ~20s)"):
        try:
            result = review_resume_session(session_id)
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
        else:
            st.session_state["review_result"] = result

# Render whatever result we have (persists across reruns via session_state).
result = st.session_state.get("review_result")
if result:
    if result.get("cached"):
        st.caption("✓ Loaded from saved result")

    st.subheader("Strengths")
    for item in result["strengths"]:
        st.markdown(f"- {item}")

    st.subheader("Weaknesses")
    for item in result["weaknesses"]:
        st.markdown(f"- {item}")

    st.subheader("Stories to share")
    for item in result["story_prompts"]:
        st.markdown(f"- {item}")