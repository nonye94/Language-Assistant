import openai
import os
import streamlit as st
from dotenv import load_dotenv
import tempfile

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
# client = st.secrets["OPENAI_API_KEY"]


def transcribe_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio.flush()

        with open(temp_audio.name, "rb") as file:
            transcript = client.audio.transcriptions.create(
                file=file,
                model="whisper-1"
            )
        return transcript.text
