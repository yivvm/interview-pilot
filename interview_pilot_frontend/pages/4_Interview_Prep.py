import streamlit as st

from lib.api import interview_prep_session
from lib.ui import inject_css

inject_css()

st.title("3 · Interview Prep")

session_id = st.session_state.get("session_id")
if not session_id:
    st.warning("Please upload a resume first on the **1 · Upload** page.")
    st.stop()

if not st.session_state.get("jd_text"):
    st.warning("Please run **3 · JD Match** first — interview prep uses that job description.")
    st.stop()

st.write(f"Prepping for: **{st.session_state.get('resume_filename', '')}**")

if st.button("Generate interview questions"):
    with st.spinner("Generating quesitons... (first run can take ~20s)"):
        try:
            result = interview_prep_session(session_id)
        except Exception as exc:
            st.error(f"Generation failed: {exc}")
        else:
            st.session_state["interview_result"] = result

result = st.session_state.get("interview_result")
if result:
    if result.get("cached"):
        st.caption("✓ Loaded from saved result")
    
    for i, q in enumerate(result["questions"], start=1):
        with st.expander(f"Q{i}. {q['question']}  ·  _{q.get('category', '')}_"):
            for bullet in q["answer_bullets"]:
                st.markdown(f"- {bullet}")
            st.caption(f"Based on: {q.get('resume_anchor', '—')}")
