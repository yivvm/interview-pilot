import streamlit as st

from lib.api import (
    interview_prep_session,
    match_resume_session,
    review_chat,
    review_resume_session,
)
from lib.ui import (
    add_message,
    get_messages,
    get_or_create_chat,
    inject_css,
    render_chat_history,
    resume_input,
)


inject_css()

st.title("Interview Pilot")

TABS = ["Resume Review", "JD Match", "Interview Prep"]
# A sidebar chat-history click can request a tab switch via "_pending_tab".
# Apply it BEFORE the radio is created (a widget's state can't be set afterward).
if "_pending_tab" in st.session_state:
    st.session_state["tab_radio"] = st.session_state.pop("_pending_tab")
choice = st.radio(
    "Section",
    TABS,
    horizontal=True,
    label_visibility="collapsed",
    key="tab_radio",
)

# ============================================================ Resume Review
if choice == "Resume Review":
    session_id = resume_input("review")
    if not session_id:
        st.markdown(
            '<div class="ip-note">Upload a resume above to begin.</div>',
            unsafe_allow_html=True,
        )
    else:
        if st.button("Analyze my resume"):
            with st.spinner("Analyzing... (first run can take ~20s)"):
                try:
                    result = review_resume_session(session_id)
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")
                else:
                    st.session_state["review_result"] = result
                    cid = get_or_create_chat("resume_review", session_id)
                    st.session_state["chats"][cid]["result"] = result

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

# ================================================================ JD Match
elif choice == "JD Match":
    session_id = resume_input("match")
    if not session_id:
        st.markdown(
            '<div class="ip-note">Upload a resume above to begin.</div>',
            unsafe_allow_html=True,
        )
    else:
        jd_text = st.text_area(
            "Paste the job description",
            value=st.session_state.get("jd_text", ""),
            height=200,
            placeholder="Paste the full job description here...",
            key="jd_text_match",
        )
        if st.button("Analyze match") and jd_text.strip():
            st.session_state["jd_text"] = jd_text
            with st.spinner("Analyzing match... (first run can take ~20s)"):
                try:
                    result = match_resume_session(session_id, jd_text)
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")
                else:
                    st.session_state["match_result"] = result
                    cid = get_or_create_chat("jd_match", session_id, jd_text)
                    st.session_state["chats"][cid]["result"] = result

        result = st.session_state.get("match_result")
        if result:
            if result.get("cached"):
                st.caption("✓ Loaded from saved result")
            st.metric("Match score", f"{result['match_score']} / 100")
            st.subheader("Matching skills")
            if result["matching_skills"]:
                st.write("  ".join(f"`{s}`" for s in result["matching_skills"]))
            else:
                st.write("_None detected_")
            st.subheader("Gaps")
            severity_emoji = {"high": "🔴", "medium": "🟠", "low": "🟡"}
            for gap in result["gaps"]:
                dot = severity_emoji.get(gap.get("severity", "").lower(), "⚪")
                st.markdown(f"{dot} **{gap['skill']}** ({gap.get('severity', '?')}) - {gap['suggestion']}")
            st.subheader("Rewrite suggestions")
            for rw in result["rewrite_suggestions"]:
                with st.container(border=True):
                    st.markdown(f"**Before:** {rw['original']}")
                    st.markdown(f"**After:** {rw['improved']}")

# =========================================================== Interview Prep
else:
    session_id = resume_input("inteview")
    if not session_id:
        st.markdown(
            '<div class="ip-note">Upload a resume above to begin.</div>',
            unsafe_allow_html=True,
        )
    else:
        jd_text = st.text_area(
            "Job description",
            value=st.session_state.get("jd_text", ""),
            height=200,
            placeholder="Paste the job description here...",
            key="jd_text_interview",
        )
        if st.button("Generate interview questions") and jd_text.strip():
            st.session_state["jd_text"] = jd_text
            with st.spinner("Generating questions... (first run can take ~20s)"):
                try:
                    result = interview_prep_session(session_id, jd_text)
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")
                else:
                    st.session_state["interview_result"] = result
                    cid = get_or_create_chat("interview_prep", session_id, jd_text)
                    st.session_state["chats"][cid]["result"] = result

        result = st.session_state.get("interview_result")
        if result:
            if result.get("cached"):
                st.caption("✓ Loaded from saved result")
            for i, q in enumerate(result["questions"], start=1):
                with st.expander(f"Q{i}. {q['question']}  ·  _{q.get('category', '')}_", expanded=(i == 1)):
                    for bullet in q["answer_bullets"]:
                        st.markdown(f"- {bullet}")
                    st.caption(f"Based on: {q.get('resume_anchor', '—')}")

# ==================== Centralized coach chat (below the tabs) ====================
st.divider()
st.subheader("Ask the coach")
st.caption(
    "- Follow up on the analysis, e.g. *“How can I make my dashboard bullet stronger?”*\n"
    "- Ask for specific, actionable advice on your resume — wording, metrics, structure, or what to highlight.\n"
    "- Ask any questions to prepare your interview."
)

active_cid = st.session_state.get("active_chat_id")
chat = st.session_state.get("chats", {}).get(active_cid) if active_cid else None
messages = get_messages(active_cid) if active_cid else []

if not chat:
    st.markdown(
        '<div class="ip-note">Run an analysis above — or pick a past chat in the sidebar — to start. '
        'You can ask about your resume, the JD match, or interview prep.</div>',
        unsafe_allow_html=True,
    )
else:
    _pretty = {"resume_review": "Resume Review", "jd_match": "JD Match", "interview_prep": "Interview Prep"}.get(chat["section"], chat["section"])
    _detail = chat.get("jd_title") or chat["filename"]
    st.caption(f"Active chat: **{_pretty} · {_detail}**")
    if st.button("Clear chat", key="clear_chat"):
        chat["messages"].clear()
        st.rerun()

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask about your resume, the match, or interview prep...")
if prompt:
    sid = st.session_state.get("session_id")
    if not active_cid:
        if not sid:
            st.warning("Upload a resume first.")
            st.stop()
        active_cid = get_or_create_chat("resume_review", sid)
    conv = st.session_state["chats"][active_cid]
    add_message(active_cid, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = review_chat(conv["session_id"], get_messages(active_cid))
            except Exception as exc:
                reply = f"Error: {exc}"
        st.markdown(reply)
    add_message(active_cid, "assistant", reply)


# Draw the sidebar chat-history list LAST — so a chat created by any button in
# this same run shows up immediately (no extra rerun).
render_chat_history()
