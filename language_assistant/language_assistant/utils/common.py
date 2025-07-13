
from utils.gpt_module import ask_gpt
from utils.whisper import transcribe_audio


def select_topic():
    level = st.selectbox("Select your level:", ["Beginner", "Intermediate", "Advanced"])
    topics_by_level = {
        "Beginner": ["Greetings", "Food", "Family", "Colors", "Numbers"],
        "Intermediate": ["Travel", "Shopping", "Weather", "Daily Routine", "Hobbies"],
        "Advanced": ["Politics", "Environment", "Technology", "Culture", "Business"]
    }

    topic_options = topics_by_level[level] + ["Other"]
    chosen_topic = st.selectbox("Choose a topic:", topic_options)

    if chosen_topic == "Other":
        custom_topic = st.text_input("Type your custom topic:")
        return custom_topic
    return chosen_topic


import streamlit as st
from pydub import AudioSegment
from io import BytesIO
from audiorecorder import audiorecorder  # Ensure this is correctly imported
from gtts import gTTS


def record_and_transcribe():
    st.header("🎙️ Speak and Learn")

    audio_data = audiorecorder("Click once to start recording. Click again to stop", "Recording...")

    if audio_data is not None and len(audio_data) > 0:
        st.success("✅ Recording complete")

        # Export AudioSegment to BytesIO
        audio_buffer = BytesIO()
        audio_data.export(audio_buffer, format="wav")
        audio_bytes = audio_buffer.getvalue()

        st.audio(audio_bytes, format="audio/wav")

        if st.button("🧠 Transcribe and Translate"):
            with st.spinner("Processing your voice..."):
                # Transcribe using Whisper
                transcribed_text = transcribe_audio(audio_bytes)
                st.write("🔤 You said:", transcribed_text)

                # Get response from GPT
                response = ask_gpt(f"Translate and explain: {transcribed_text}")
                st.write("🧠 GPT says:")
                st.write(response)
                # Convert GPT response to speech
                tts = gTTS(response)
                tts_audio = BytesIO()
                tts.write_to_fp(tts_audio)
                tts_audio.seek(0)

                st.audio(tts_audio, format='audio/mp3', start_time=0)
