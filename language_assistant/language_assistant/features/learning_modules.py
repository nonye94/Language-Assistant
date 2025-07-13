import streamlit as st
from utils.gpt_module import ask_gpt
from utils.common import select_topic
from utils.database import save_quiz_score, save_learning_progress
import json
import time

from streamlit.components.v1 import html


def scroll_bottom():
    js = """
    <script>
        window.parent.document.querySelector('section.main').scrollTo(0, window.parent.document.querySelector('section.main').scrollHeight);
    </script>
    """
    html(js, height=0)


def show_learning_modules_interface():
    st.header("📘 Learning Modules")

    module = st.selectbox("Choose a module", [
        "💬 AI Practice Chat",
        "❓ Vocabulary Quiz",
        "📝 Fill in the Blanks",
        "🔤 Grammar"
    ])

    # 💬 Chat Module
    if module == "💬 AI Practice Chat":
        st.subheader("Practice Chat with AI Tutor")
        user_input = st.text_input("Say something in Spanish:")

        if user_input:
            with st.spinner("AI Tutor is thinking..."):
                response = ask_gpt(
                    f"You're a Spanish tutor. Respond to this in English and Spanish and explain anything tricky in "
                    f"English:\n\n{user_input}")
            st.write("💬 AI Tutor:")
            st.write(response)

    elif module == "❓ Vocabulary Quiz":
        st.header("Vocabulary Quiz")

        # Clear previous quiz state if quiz is complete
        if 'quiz_index' in st.session_state and st.session_state.quiz_index >= len(
                st.session_state.get('quiz_questions', [])):
            if st.session_state.get('quiz_questions'):
                del st.session_state.quiz_questions
                del st.session_state.quiz_index
                del st.session_state.quiz_score

        topic = select_topic()
        num_questions = st.slider("Number of questions", 1, 10, 5)

        if 'quiz_questions' not in st.session_state:
            if st.button("Start Quiz"):
                if topic:
                    with st.spinner("Preparing questions..."):
                        prompt = f"""Create a Spanish vocabulary multiple-choice quiz with {num_questions} questions about {topic}. Ask the question using English Language.
                                              Return ONLY a valid JSON array where each question is an object with these exact keys: 
                                              "question" (string), "options" (array of strings), "answer" (string). 
                                              Example format: [{{"question": "...", "options": ["...", "..."], "answer": "..."}}]"""

                        questions = ask_gpt(prompt)
                    try:
                        parsed_questions = json.loads(questions)
                        if isinstance(parsed_questions, list) and len(parsed_questions) > 0:
                            st.session_state.quiz_questions = parsed_questions
                            st.session_state.quiz_index = 0
                            st.session_state.quiz_score = 0
                            st.session_state.quiz_start_time = time.time()
                            st.rerun()
                        else:
                            st.error("Received empty or invalid question list")
                    except json.JSONDecodeError as e:
                        st.error(f"Invalid JSON format: {str(e)}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            question = st.session_state.quiz_questions[st.session_state.quiz_index]
            st.write(f"Q{st.session_state.quiz_index + 1}: {question['question']}")
            choice = st.radio("Choose:", question['options'], key=f"choice_{st.session_state.quiz_index}")
            if st.button("Submit Answer", key=f"submit_{st.session_state.quiz_index}"):
                if choice == question['answer']:
                    st.session_state.quiz_score += 1
                    st.success("Correct!")

                else:
                    st.error(f"Wrong! Correct answer: {question['answer']}")
                st.session_state.quiz_index += 1
                if st.session_state.quiz_index < len(st.session_state.quiz_questions):
                    st.rerun()
                else:
                    # Quiz is complete - show results but don't delete state yet
                    st.success(
                        f"Quiz Complete! You scored {st.session_state.quiz_score} out of {len(st.session_state.quiz_questions)}")
                    quiz_duration = time.time() - st.session_state.quiz_start_time
                    minutes, seconds = divmod(quiz_duration, 60)

                    save_quiz_score(st.session_state.username, st.session_state.quiz_score,
                                    len(st.session_state.quiz_questions), "Vocabulary")

                    save_learning_progress(st.session_state.username, "Vocabulary", st.session_state.quiz_score,
                                           len(st.session_state.quiz_questions),
                                           quiz_duration)
                    if st.button("Start New Quiz"):
                        # Only clear the state when user explicitly asks for a new quiz
                        del st.session_state.quiz_questions
                        del st.session_state.quiz_index
                        del st.session_state.quiz_score
                        st.rerun()
    elif module == "🔤 Grammar":
        st.header("Grammar Quiz")

        # Clear previous quiz state if quiz is complete
        if 'quiz_index' in st.session_state and st.session_state.quiz_index >= len(
                st.session_state.get('quiz_questions', [])):
            if st.session_state.get('quiz_questions'):
                del st.session_state.quiz_questions
                del st.session_state.quiz_index
                del st.session_state.quiz_score

        topic = select_topic()
        num_questions = st.slider("Number of questions", 1, 10, 5)

        if 'quiz_questions' not in st.session_state:
            if st.button("Start Quiz"):
                if topic:
                    with st.spinner("Preparing questions..."):
                        prompt = f"""Create a Spanish grammar multiple-choice quiz with {num_questions} questions about {topic}. 
                                                Return ONLY a valid JSON array where each question is an object with these exact keys: 
                                                "question" (string), "options" (array of strings), "answer" (string). 
                                                Example format: [{{"question": "...", "options": ["...", "..."], "answer": "..."}}]"""

                        questions = ask_gpt(prompt)
                    try:
                        parsed_questions = json.loads(questions)
                        if isinstance(parsed_questions, list) and len(parsed_questions) > 0:
                            st.session_state.quiz_questions = parsed_questions
                            st.session_state.quiz_index = 0
                            st.session_state.quiz_score = 0
                            st.session_state.quiz_start_time = time.time()
                            st.rerun()
                        else:
                            st.error("Received empty or invalid question list")
                    except json.JSONDecodeError as e:
                        st.error(f"Invalid JSON format: {str(e)}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            question = st.session_state.quiz_questions[st.session_state.quiz_index]
            st.write(f"Q{st.session_state.quiz_index + 1}: {question['question']}")
            choice = st.radio("Choose:", question['options'], key=f"choice_{st.session_state.quiz_index}")
            if st.button("Submit Answer", key=f"submit_{st.session_state.quiz_index}"):
                if choice == question['answer']:
                    st.session_state.quiz_score += 1
                    st.success("Correct!")
                else:
                    st.error(f"Wrong! Correct answer: {question['answer']}")
                st.session_state.quiz_index += 1
                if st.session_state.quiz_index < len(st.session_state.quiz_questions):
                    st.rerun()
                else:
                    # Quiz is complete - show results but don't delete state yet
                    st.success(
                        f"Quiz Complete! You scored {st.session_state.quiz_score} out of {len(st.session_state.quiz_questions)}")
                    quiz_duration = time.time() - st.session_state.quiz_start_time
                    minutes, seconds = divmod(quiz_duration, 60)

                    save_quiz_score(st.session_state.username, st.session_state.quiz_score,
                                    len(st.session_state.quiz_questions), "Grammar")
                    save_learning_progress(st.session_state.username, "Grammar", st.session_state.quiz_score,
                                           len(st.session_state.quiz_questions),
                                           quiz_duration)
                    if st.button("Start New Quiz"):
                        # Only clear the state when user explicitly asks for a new quiz
                        del st.session_state.quiz_questions
                        del st.session_state.quiz_index
                        del st.session_state.quiz_score
                        st.rerun()
    elif module == "📝 Fill in the Blanks":
        st.subheader("Fill in the Blanks Exercise")

        # Clear previous exercise state if exercise is complete
        if 'exercise' in st.session_state and all(st.session_state.user_answers):
            del st.session_state.exercise
            del st.session_state.exercise_index
            del st.session_state.exercise_score
            del st.session_state.exercise_start_time
            del st.session_state.user_answers

        topic = select_topic()
        num_questions = st.slider("Number of questions", 1, 10, 5)

        if st.button("Generate Exercise"):
            if topic:
                with st.spinner("Preparing questions..."):
                    prompt = f"""Generate a fill-in-the-blank Spanish exercise with {num_questions} sentences about {topic}. 
                                    Return a VALID JSON array where each element is an object with "sentence" and "answer" properties.
                                    Example:
                                    [
                                        {{"sentence": "El ___ es azul.", "answer": "cielo"}},
                                        {{"sentence": "Me gusta comer ___.", "answer": "manzanas"}}
                                    ]
                                    Only return the JSON array, nothing else."""
                    exercise = ask_gpt(prompt)
            try:
                st.session_state.exercise = json.loads(exercise)
                st.session_state.exercise_index = 0
                st.session_state.exercise_score = 0
                st.session_state.exercise_start_time = time.time()
                st.session_state.user_answers = [""] * num_questions  # Initialize empty answers list
                st.rerun()
            except Exception as e:
                st.error(f"Could not parse exercise: {e}")

        if "exercise" in st.session_state:
            all_filled = True  # Assume all are filled initially
            current_score = 0
            for i, item in enumerate(st.session_state.exercise):
                user_answer = st.text_input(f"{i + 1}. {item['sentence']}", key=f"fill_{i}")
                st.session_state.user_answers[i] = user_answer  # Store the answer

                if user_answer.lower().strip() == item['answer'].lower():
                    current_score += 1
                    st.success("Correct!")
                elif user_answer:
                    st.warning(f"Oops! Correct answer: {item['answer']}")

                # If any answer is still empty, set all_filled to False
                if not user_answer.strip():
                    all_filled = False

            # Update the session state score
            st.session_state.exercise_score = current_score
            # Check if all answers are filled
            if all_filled:
                st.success("🎉 You've completed the exercise!")
                st.write(f"Your score: {st.session_state.exercise_score}/{len(st.session_state.exercise)}")

                # Calculate time taken if you want to show that
                time_taken = time.time() - st.session_state.exercise_start_time
                st.write(f"Time taken: {int(time_taken)} seconds")
                save_quiz_score(st.session_state.username, st.session_state.exercise_score,
                                len(st.session_state.exercise), "Writing")
                save_learning_progress(st.session_state.username, "Writing", st.session_state.exercise_score,
                                       len(st.session_state.exercise),
                                       time_taken)

            if st.button("Start New Quiz"):
                # Only clear the state when user explicitly asks for a new quiz
                del st.session_state.exercise
                del st.session_state.exercise_index
                del st.session_state.exercise_score
                del st.session_state.exercise_start_time
                del st.session_state.user_answers
                st.rerun()
