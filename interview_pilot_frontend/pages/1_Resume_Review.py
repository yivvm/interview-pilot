import streamlit as st

from lib.api import review_chat, review_resume_session
from lib.ui import (
    add_message,
    get_messages,
    get_or_create_chat,
    inject_css, 
    render_chat_history, 
    resume_input
)

SECTION = "resume_review"

inject_css()
render_chat_history()

st.title("1 · Resume Review")

session_id = resume_input("review")
if not session_id:
    st.info("Upload aresume above to begin")
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
            get_or_create_chat(SECTION, session_id)
            st.rerun()   # redraw sidebar so the new item shows immediately

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


# --- Chat: ask the coach follow-up questions about the resume ----------
st.divider()
st.subheader("Ask the coach")
st.caption(
    "- Follow up on the review, e.g. *“How can I make my dashboard bullet stronger?”*\n"
    "- Ask for specific, actionable advice on your resume — wording, metrics, structure, or what to highlight."
)

# Show the active conversation (set by Analyze, by the first message below,
# or by clicking an item in the sidebar history.)
active_cid = st.session_state.get("active_chat_id")
messages = get_messages(active_cid) if active_cid else []
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box pinned at the bottom; returns the text when the user hits Enter.
prompt = st.chat_input("Ask about your resume...")
if prompt:
    # Target the active conversation; create one for the current resume if none.
    cid = st.session_state.get("active_chat_id") or get_or_create_chat(SECTION, session_id)
    conv = st.session_state["chats"][cid]

    # 1. Record + show the user's message.
    add_message(cid, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call the backend with the full history; show the reply.
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = review_chat(conv["session_id"], get_messages(cid))
            except Exception as exc:
                reply = f"Error: {exc}"
        st.markdown(reply)
    
    # 3. Persist the assistant turn so it replays on the next rerun.
    add_message(cid, "assistant", reply)