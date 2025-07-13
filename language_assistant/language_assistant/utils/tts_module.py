from gtts import gTTS
import os
import tempfile
import streamlit as st


def speak_text(text, lang='es'):
    tts = gTTS(text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        st.audio(fp.name, format='audio/mp3')
