import streamlit as st

import chat_service

USER_ID = "nitish"  # a single, hardcoded user

st.set_page_config(page_title="CampusX Assistant", page_icon="🎓")

# st.session_state is Streamlit's UI memory (not the ADK session!).
# We only use it to remember which ADK session is currently open.
if "session_id" not in st.session_state:
    st.session_state.session_id = None


# ---------- Sidebar: list of sessions ----------
with st.sidebar:
    st.title("🎓 CampusX Assistant")
    st.caption(f"Logged in as: {USER_ID}")

    if st.button("➕ New chat", width="stretch"):
        st.session_state.session_id = chat_service.create_session(USER_ID)
        st.rerun()

    st.subheader("Your chats")
    for s in chat_service.list_sessions(USER_ID):
        is_active = s["id"] == st.session_state.session_id
        if st.button(
            s["title"],
            key=s["id"],
            width="stretch",
            type="primary" if is_active else "secondary",
        ):
            st.session_state.session_id = s["id"]
            st.rerun()


# ---------- Chat area ----------
session_id = st.session_state.session_id

if session_id is None:
    st.info("Start a new chat or pick one from the sidebar.")
else:
    for msg in chat_service.get_messages(USER_ID, session_id):
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])

prompt = st.chat_input("Type a message...")
if prompt:
    if session_id is None:  # first message creates a session
        session_id = chat_service.create_session(USER_ID)
        st.session_state.session_id = session_id

    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = chat_service.send_message(USER_ID, session_id, prompt)
        st.markdown(reply)

    st.rerun()  # refresh the sidebar so the new title shows up