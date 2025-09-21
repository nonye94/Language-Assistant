import streamlit as st
from datetime import datetime
from utils.database import  get_user_quiz_scores


def get_quiz_history():

    st.title("Quiz Score History")

    if st.session_state.username:
        scores = get_user_quiz_scores(st.session_state.username)

        if scores:
            st.markdown(f"Showing latest **{len(scores)}** scores for **{st.session_state.username}**")
            for i, (ts, sc, tq, quiz_type) in enumerate(scores, 1):
                human_date = datetime.fromisoformat(ts).strftime("%b %d, %Y at %I:%M %p")
                st.write(f"**{i}.** *{quiz_type}* — **{sc}/{tq}** — 📅 {human_date}")
        else:
            st.info("No scores found.")
    else:
        st.warning("Please log in to view your quiz history.")
