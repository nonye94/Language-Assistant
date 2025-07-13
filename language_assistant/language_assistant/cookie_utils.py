

import streamlit as st
from streamlit.components.v1 import html
import time


def set_cookie(name, value, days=7):
    js = f"""
    <script>
    function setCookie(name, value, days) {{
        var expires = "";
        if (days) {{
            var date = new Date();
            date.setTime(date.getTime() + (days*24*60*60*1000));
            expires = "; expires=" + date.toUTCString();
        }}
        document.cookie = name + "=" + (value || "")  + expires + "; path=/";
    }}
    setCookie("{name}", "{value}", {days});
    </script>
    """
    html(js)


def get_cookie(name):
    # Create a unique key for this cookie request
    key = f"cookie_{name}_{time.time()}"

    # JavaScript to get the cookie and store it in Streamlit's session state
    js = f"""
    <script>
    function getCookie(name) {{
        const value = `; ${{document.cookie}}`;
        const parts = value.split(`; ${{name}}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }}
    const cookieValue = getCookie("{name}");
    window.parent.document.querySelector('iframe').contentWindow.streamlitApi.runScript(
        {{
            'script': `st.session_state['{key}'] = "${{cookieValue}}";`
        }}
    );
    </script>
    """
    html(js)

    # Wait briefly for the JavaScript to execute
    time.sleep(0.1)

    # Return the cookie value from session state
    return st.session_state.get(key, "")