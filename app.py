import os

import streamlit as st
from crud import display_crud_operations
from visualizations import display_visualizations
from styles import set_background_gif, set_title_style, set_container_style, hide_topbar   # Imported styling functions

def main():
    hide_topbar()

    gif_path = os.path.join("assets", "background1.gif")
    # set_background_gif(gif_path=gif_path)

    # Set title style
    set_title_style()

    # set_container_style()

    # Display the styled title
    st.markdown('<h1 class="title">Banking System Dashboard with CRUD and Visualizations</h1>', unsafe_allow_html=True)
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select Page", ["CRUD Operations", "Visualizations"])

    if page == "CRUD Operations":
        display_crud_operations()
    elif page == "Visualizations":
        display_visualizations()

if __name__ == "__main__":
    st.set_page_config(page_title="Banking System Dashboard", page_icon="🏦")
    main()
