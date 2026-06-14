import streamlit as st

from lib.api import upload_resume

st.title(" 1 · Upload")
st.write("Upload your resume (PDF or DOCX). We'll extract the text for anlaysis.")
uploaded = st.file_uploader("Choose a resume", type=["pdf", "docx"])

if uploaded is not None and st.button("Upload & parse"):
    # ... only create a session if this file hasn't been uploaded already
    if st.session_state.get("uploaded_name") != uploaded.name:
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
                # Store in session_state so other pages + the sidebar can see it.
                st.session_state["session_id"] = result["session_id"]
                st.session_state["resume_filename"] = result["resume_filename"]
                st.session_state["uploaded_name"] = uploaded.name 
                st.success(f"Uploaded! Session ID: {result['session_id']}")
                with st.expander("Preview extracted text"):
                    st.text(result["resume_preview"])