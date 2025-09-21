import secrets
import streamlit as st
from utils.database import login_user, register_user, save_token
from cookie_utils import set_cookie
from streamlit.components.v1 import html
import re


def show_login():
    # Centered logo

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login"):
        if login_user(username, password):
            token = secrets.token_urlsafe(16)
            save_token(username, token)
            set_cookie("session_token", token)
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid credentials")


def validate_password(password):
    if len(password) < 6:
        return "Password should be at least 6 characters long."
    elif not re.search("[a-z]", password):
        return "Password should have at least one lowercase letter."
    elif not re.search("[A-Z]", password):
        return "Password should have at least one uppercase letter."
    elif not re.search("[0-9]", password):
        return "Password should have at least one digit."
    elif not re.search("[^A-Za-z0-9]", password):
        return "Password should have at least one special character."
    else:
        return None


def show_register():
    st.subheader("Register")
    with st.form("register_form"):
        firstname = st.text_input("Enter your first Name", key="reg_firstname")
        lastname = st.text_input("Enter your last Name", key="reg_lastname")
        username = st.text_input("Choose a username", key="reg_user")
        password = st.text_input("Choose a password", type="password", key="reg_pass")
        confirm_password = st.text_input("Confirm password", type="password", key="reg_confirm_pass")
        submitted = st.form_submit_button("Register")

    if submitted:
        error = validate_password(password)
        if error:
            st.error(error)
        elif password != confirm_password:
            st.error("Passwords do not match.")
        elif not register_user(username, password, firstname, lastname):
            st.error("Username already exists.")
        else:
            token = secrets.token_urlsafe(16)
            save_token(username, token)
            set_cookie("session_token", token)
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()


def show_logout():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Logged out!")
        st.rerun()
