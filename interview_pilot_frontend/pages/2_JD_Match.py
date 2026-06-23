import streamlit as st

from lib.api import match_resume_session
from lib.ui import inject_css, resume_input

inject_css()

st.title("2 · Job Description Match")

session_id = resume_input("match")
if not session_id:
    st.markdown(
        '<div class="ip-note">Upload a resume above to begin.</div>',
        unsafe_allow_html=True,
    )
    st.stop()

st.write(f"Matching resume: **{st.session_state.get('resume_filename', '')}**")

jd_text = st.text_area(
    "Paste the job description",
    value=st.session_state.get("jd_text", ""),
    height=200,
    placeholder="Paste the full job description here...",
)

if st.button("Analyze match") and jd_text.strip():
    st.session_state["jd_text"] = jd_text  # remember JD for Section 3
    with st.spinner("Analyzing match... (first run can take ~20s)"):
        try:
            result = match_resume_session(session_id, jd_text)
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
        else:
            st.session_state["match_result"] = result

result = st.session_state.get("match_result")
if result:
    if result.get("cached"):
        st.caption("✓ Loaded from saved result")

    # Score
    st.metric("Match score", f"{result['match_score']} / 100")

    # Maching skills as chips
    st.subheader("Matching skills")
    if result["matching_skills"]:
        st.write("  ".join(f"`{s}`" for s in result["matching_skills"]))
    else:
        st.write("_None detected_")
    
    # Gaps with severity colot
    st.subheader("Gaps")
    severity_emoji = {"high": "🔴", "medium": "🟠", "low": "🟡"}
    for gap in result["gaps"]:
        dot = severity_emoji.get(gap.get("severity", "").lower(), "⚪")
        st.markdown(f"{dot} **{gap['skill']}** ({gap.get('severity', '?')}) - {gap['suggestion']}")

    # Rewrite suggestions as before/after
    st.subheader("Rewrite suggestions")
    for rw in result["rewrite_suggestions"]:
        with st.container(border=True):
            st.markdown(f"**Before:** {rw['original']}")
            st.markdown(f"**After:** {rw['improved']}")
