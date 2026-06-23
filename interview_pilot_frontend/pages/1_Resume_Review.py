import streamlit as st

from lib.api import review_chat, review_resume_session
from lib.ui import inject_css, render_chat_history, resume_input

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
st.caption("Follow up on the review, e.g. *“How can I make my dashboard bullet stronger?”*")

# Running conversation lives in session_state so it survives reruns.
if "review_chat" not in st.session_state:
    st.session_state["review_chat"] = []


# Replay the conversation so far.
for msg in st.session_state["review_chat"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box pinned at the bottom; returns the text when the user hits Enter.
prompt = st.chat_input("Ask about your resume...")
if prompt:
    # 1. Record + show the user's message.
    st.session_state["review_chat"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call the backend with the full history; show the reply.
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply = review_chat(session_id, st.session_state['review_chat'])
            except Exception as exc:
                reply = f"Error: {exc}"
        st.markdown(reply)
    
    # 3. Persist the assistant turn so it replays on the next rerun.
    st.session_state["review_chat"].append({"role": "assistant", "content": reply})