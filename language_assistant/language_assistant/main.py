import streamlit as st

# Auth
from features.auth import show_login, show_register, show_logout
from cookie_utils import get_cookie
from utils.database import get_username_by_token

# Database setup
from utils.database import (
    init_db, create_flashcard_tables, create_learning_history_table,
    init_quiz_table
)

# App features
from features.chat import show_chat_interface
from features.flashcards import show_flashcard_interface, show_review_flashcard_interface
from features.learning_modules import show_learning_modules_interface
from utils.common import record_and_transcribe
from features.quiz_history import get_quiz_history
from features.recommendation import user_dashboard


def setup_database():
    init_db()
    create_flashcard_tables()
    create_learning_history_table()
    init_quiz_table()


def restore_login_from_cookie():
    token = get_cookie("session_token")
    if token:
        username = get_username_by_token(token)
        if username:
            st.session_state.logged_in = True
            st.session_state.username = username


def show_dashboard():
    st.success(f"Welcome back, {st.session_state.username}!")
    st.header("Your Language Dashboard")
    st.title("🇪🇸 Learn Spanish with AI")

    option = st.sidebar.selectbox(
        "Choose a feature",
        [
            "Chat with Assistant", "Generate Flashcards", "Review Flashcards",
            " Speak and Learn", "Learning Modules", "Quiz History", "Recommendation"
        ]
    )

    match option:
        case "Chat with Assistant":
            show_chat_interface()
        case "Generate Flashcards":
            show_flashcard_interface()
        case "Review Flashcards":
            show_review_flashcard_interface()
        case "Speak and Learn":
            record_and_transcribe()
        case "Learning Modules":
            show_learning_modules_interface()
        case "Quiz History":
            get_quiz_history()
        case "Recommendation":
            user_dashboard(st.session_state.username)


# Main logic
def main():
    setup_database()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    if not st.session_state.logged_in:
        restore_login_from_cookie()

    st.title("Language Learning Assistant")

    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            show_login()
        with tab2:
            show_register()
    else:
        show_logout()
        show_dashboard()


if __name__ == "__main__":
    main()
