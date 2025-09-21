import streamlit as st
from utils.database import get_due_flashcards, update_card_schedule
from utils.flashcards import generate_flashcards
from utils.database import save_flashcards
from utils.tts_module import speak_text
from sm2 import sm2


def show_flashcard_interface():
    st.header("Topic-Based Flashcards")
    topic = st.text_input("Enter a topic (e.g., Food, Travel, Family):")
    if not topic:
        st.warning("Please enter a topic before proceeding.")
        st.stop()
    num = st.slider("How many flashcards?", min_value=5, max_value=100, step=5)

    # Generate flashcards and store them
    if st.button("Generate"):
        with st.spinner("Creating flashcards..."):
            cards = generate_flashcards(topic, batch_size=num, max_batches=1)
            st.session_state['cards'] = cards
            # Save flashcards to DB for the logged-in user
            save_flashcards(st.session_state.username, cards)

    # Display stored flashcards if available
    if 'cards' in st.session_state:
        for idx, card in enumerate(st.session_state['cards']):
            st.markdown(f"**Word:**  {card['word']}")
            st.markdown(f"- Meaning: {card['meaning']}")
            st.markdown(f"- Example: {card['example']}")
            if st.button(f"🔊 Pronounce '{card['word']}'", key=f"{card['word']}_{idx}"):
                speak_text(card['word'], lang='es')


def show_review_flashcard_interface():
    st.header("Review Due Flashcards")
    if 'flashcard_feedback' in st.session_state:
        st.toast(st.session_state.flashcard_feedback, icon='🎉')
        del st.session_state.flashcard_feedback

    if 'flashcard_warning' in st.session_state and st.session_state.flashcard_warning:
        st.toast(st.session_state.flashcard_warning, icon=":material/sentiment_sad:")
        st.session_state.flashcard_warning = None

    due_cards = get_due_flashcards(st.session_state.username)

    if due_cards:
        for card in due_cards:
            card_id, word, meaning, example, ease, reps, interval = card
            st.markdown(f"**Word:** {word}")
            st.markdown(f"- Meaning: {meaning}")
            st.markdown(f"- Example: {example}")
            if st.button(f"🔊 Hear {word}", key=f"sound_{card_id}"):
                speak_text(word)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("I remembered", key=f"correct_{card_id}"):
                    ease_new, reps_new, interval_new, next_review = sm2(ease, reps, interval, quality=5)
                    update_card_schedule(card_id, ease_new, reps_new, interval_new, next_review)
                    st.session_state.flashcard_feedback = f"Great! Next review in {interval_new} day(s)."
                    st.rerun()

            with col2:
                if st.button("I forgot", key=f"wrong_{card_id}"):
                    ease_new, reps_new, interval_new, next_review = sm2(ease, reps, interval, quality=2)
                    update_card_schedule(card_id, ease_new, reps_new, interval_new, next_review)
                    st.session_state.flashcard_warning = f"No worries — you’ll see it in {interval_new} day(s). !"
                    st.rerun()
    else:
        st.info("No flashcards due for review. Come back later!")
