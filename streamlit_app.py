import streamlit as st
from streamlit_extras.switch_page_button import switch_page


def main():
    st.markdown("<h2 style='text-align: center;'>Welcome back!</h2>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>BioDesign Copilot</h1>", unsafe_allow_html=True)
    # st.markdown("<h3 style='text-align: center;'>Need Statement Assistant (Coming Soon) </h3>", unsafe_allow_html=True)
    # st.markdown("<h3 style='text-align: center;'>Observation Assistant</h3>", unsafe_allow_html=True)

    assistant = st.selectbox(
        'Choose an assistant',
        ('Observation Assistant', 'Need Statement Assistant (Coming Soon)'),
        index=0  # 0 is the index for the default option 'Observation Assistant'
    )

    # Login Form
    st.write("")
    st.write("")
    st.write("Login:")
    username = st.text_input("Username:", key="username")
    password = st.text_input("Password:", type="password", key="password")
    stay_logged_in = st.checkbox("Stay logged in")

    if st.button("Submit"):
        if username == "ana" and password == "123":
            st.success("Login successful")
            st.session_state["login_status"] = "success"
            st.rerun()
        else:
            st.error("Try again please")

if __name__ == "__main__":
    st.set_page_config(initial_sidebar_state="collapsed")

    if "login_status" not in st.session_state:
        st.session_state["login_status"] = "not_logged_in"

    if st.session_state["login_status"] == "success":
        # st.query_params(page="main_menu")
        # st.query_params[''] = "main_menu"
        # # st.page_link("pages/main_menu.py")
        # st.rerun()
        switch_page("main_menu")
    else:
        main()
