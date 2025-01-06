# styles.py

import streamlit as st
import base64
import os


# styles.py

def set_background_gif(gif_path=None, gif_url=None):
    """
    Sets a background GIF for the Streamlit app with an optional semi-transparent overlay.

    Parameters:
    - gif_path (str): Path to the local GIF file.
    - gif_url (str): URL of the online GIF.
    """
    if gif_url:
        background_style = f"""
        <style>
        body {{
            background-image: url("{gif_url}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        /* Overlay */
        .stApp {{
            background: rgba(255, 255, 255, 0.8);
        }}
        </style>
        """
    elif gif_path:
        if not os.path.exists(gif_path):
            st.warning(f"Background GIF not found at {gif_path}.")
            return
        # Read the GIF file and encode it in base64
        with open(gif_path, "rb") as gif_file:
            encoded_gif = base64.b64encode(gif_file.read()).decode()
        background_style = f"""
        <style>
        body {{
            background-image: url("data:image/gif;base64,{encoded_gif}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        /* Overlay */
        .stApp {{
            background: rgba(255, 255, 255, 0.1);
        }}
        </style>
        """
    else:
        st.warning("No background GIF provided.")
        return

    st.markdown(background_style, unsafe_allow_html=True)


def set_title_style():
    """
    Styles the main title of the Streamlit app with an elegant, technology-inspired look.
    """
    title_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@700&display=swap');

    .title {
        font-family: 'Roboto Slab', serif;
        color: #FFFFFF;
        font-size: 65px;
        text-align: center;
        text-shadow: 2px 2px #000000;
    }
    </style>
    """
    st.markdown(title_style, unsafe_allow_html=True)

# styles.py

def set_container_style():
    """
    Styles the Streamlit containers for better aesthetics.
    """
    container_style = """
    <style>
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    .stButton>button {
        border-radius: 10px;
        background-color: #00BFFF;
        color: white;
    }
    </style>
    """
    st.markdown(container_style, unsafe_allow_html=True)


def hide_topbar():
    """
    Hides the Streamlit topbar, including the 'Deploy' button and the three-dotted menu.
    """
    hide_style = """
    <style>
    /* Hide Streamlit's main menu */
    #MainMenu {visibility: hidden;}

    /* Hide Streamlit's header */
    header {visibility: hidden;}

    /* Hide Streamlit's footer */
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

