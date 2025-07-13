import streamlit as st
from utils.common import select_topic
from utils.gpt_module import ask_gpt_chat
from utils.tts_module import speak_text


def show_chat_interface():
    st.header("Ask anything in English or Spanish!")

    user_input = select_topic()

    # Only ask GPT and save to session state
    if st.button("Ask"):
        with st.spinner("Thinking..."):
            response = ask_gpt_chat(user_input)
            st.session_state['response'] = response  # 💾 Save response

    # Only show and speak if there's something stored
    if 'response' in st.session_state:
        st.success("Response:")
        st.write(st.session_state['response'])

        if st.button("🔊 Hear it in Spanish"):
            with st.spinner("Processing audio..."):
                speak_text(st.session_state['response'], lang='es')
