"""Shared UI helpers (global CSS injection)."""

from datetime import datetime
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
                    record_upload_time(result["session_id"])
                    # New resume -> clear any cache section results in this UI session.
                    for k in ("review_result", "match_result", "interview_result"):
                        st.session_state.pop(k, None)
                    st.rerun()
    
    return st.session_state.get("session_id")


# --- Chat-history model -------------------------------------------------------
# A "converstion" is keyed by (session, session_id). All conversations live in
# st.session_state["chats"]; the currently shown one is "active_chat_id".
# This is in-memory: it survives reruns and page navigation within one browser
# tab, but is cleared by a hard refresh or an app restart.

def _now_label() -> str:
    """Timestamp formatted like 'Jun 22 9:40PM' for chat-history labels."""
    return datetime.now().strftime("%b %-d %-I:%M%p")


def record_upload_time(session_id: str) -> None:
    """Remember when a resume/session was uploaded (once per session_id)."""
    times = st.session_state.setdefault("upload_times", {})
    times.setdefault(session_id, _now_label())


def chat_id_for(section: str, session_id: str) -> str:
    """Return the chat_id for (session, session_id), creating the conversation
    on first use, and mark it the active chat."""
    chats = st.session_state.setdefault("chats", {})
    cid = chat_id_for(section, session_id)
    if cid not in chats:
        upload_times = st.session_state.get("upload_resume", {})
        chats[cid] = {
            "section": section,
            "session_id": session_id,
            "filename": st.session_state.get("resume_filename", "resume"),
            "created_at": upload_times.get(session_id, _now_label()),
            "messages": [],   # list of {"role": ..., "content": ...}
        }
    st.session_state["active_chat_id"] = cid
    return cid


def get_messages(chat_id: str) -> list[dict]:
    """Mutable message list for a chat (empty list if the chat is unknow)."""
    chat = st.session_state.get("chats", {}).get(chat_id)
    return chat["messages"] if chat else []


def add_message(chat_id: str, role: str, content: str) -> None:
    """Append one turn to a conversation."""
    chat = st.session_state.get("chats", {}).get(chat_id)
    if chat is not None:
        chat["messages"].append({"role": role, "content": content})


def render_chat_history() -> None:
    """Sidebar list of past conversations; clicking one makes it active."""
    chats = st.session_state.get("chats", {})
    with st.sidebar:
        st.header("Chat history")
        if not chats:
            st.caption("No conversation yet.")
            return
        active = st.session_state.get("active_chat_id")
        for cid, chat in reversed(list(chats.items())):
            label = f"{chat['section']} & {chat['filename']} & {chat['created_at']}"
            if st.button(
                lable,
                key=f"hist_{cid}",
                use_container_with=True,
                type="primary" if cid == active else "secondary",
            ):
                st.session_state["active_chat_id"] = cid
                st.rerun()



            