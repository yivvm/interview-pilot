import streamlit as st

from lib.api import interview_prep_session
from lib.ui import inject_css, resume_input

inject_css()

st.title("3 · Interview Prep")

session_id = resume_input("inteview")
if not session_id:
    st.info("Upload a resume above to begin.")
    st.stop()

st.write(f"Prepping for: **{st.session_state.get('resume_filename', '')}**")

jd_text = st.text_area(
    "Job description",
    value=st.session_state.get("jd_text", ""),
    height=200,
    placeholder="Paste the job description here...",
)

if st.button("Generate interview questions") and jd_text.strip():
    st.session_state["jd_text"] = jd_text   # reuse
    with st.spinner("Generating questions... (first run can take ~20s)"):
        try:
            result = interview_prep_session(session_id, jd_text)
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
