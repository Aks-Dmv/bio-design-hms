import streamlit as st
from streamlit_extras.switch_page_button import switch_page


def main():
    st.markdown("<h2 style='text-align: center;'>Welcome back!</h2>", unsafe_allow_html=True)
        # Your logo URL
    logo_url = "https://raw.githubusercontent.com/Aks-Dmv/bio-design-hms/main/Logo-HealthTech.png"  # Replace with the actual URL of your logo
    
    # Display the title with the logo below it
    st.markdown(
        f"""
        <div style="text-align: center;">
            <h1>HealthTech WayFinder</h1>
             <img src="{logo_url}" alt="Logo" style="width:350px; height:auto;">
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # st.markdown("<h1 style='text-align: center;'>HealthTech WayFinder</h1>", unsafe_allow_html=True)
    # st.markdown("<h3 style='text-align: center;'>Need Statement Assistant (Coming Soon) </h3>", unsafe_allow_html=True)
    # st.markdown("<h3 style='text-align: center;'>Observation Assistant</h3>", unsafe_allow_html=True)

    assistant = st.selectbox(
        'Choose an assistant',
        ('Observation Assistant', 'Need Statement Assistant (Coming Soon)'),
        index=0  # 0 is the index for the default option 'Observation Assistant'
    )

    
    st.write("")
    if st.button("Sign In"):
        st.info("New licenses coming soon!")
    
    # # Login Form

    # st.write("")
    # st.write("Login:")
    # username = st.text_input("Username:", key="username")
    # password = st.text_input("Password:", type="password", key="password")
    # stay_logged_in = st.checkbox("Stay logged in")

    # user_list = st.secrets["login-credentials"]

    # if st.button("Submit"):
    #     for user_dict in user_list:
    #         if username == user_dict["username"] and password == user_dict["password"]:
    #             st.success("Login successful")
    #             st.session_state["login_status"] = "success"
    #             st.rerun()
    #     st.error("Try again please")

    with st.form(key="login_form"):
        st.write("Login:")
        username = st.text_input("Username:", key="username")
        password = st.text_input("Password:", type="password", key="password")
        stay_logged_in = st.checkbox("Stay logged in")
    
        submit_button = st.form_submit_button("Submit")
    
    if submit_button:
        user_list = st.secrets["login-credentials"]
        for user_dict in user_list:
            if username == user_dict["username"] and password == user_dict["password"]:
                st.success("Login successful")
                st.session_state["login_status"] = "success"
                st.rerun()
        st.error("Try again please")

# if __name__ == "__main__":
#     st.set_page_config(initial_sidebar_state="collapsed")

#     if "login_status" not in st.session_state:
#         st.session_state["login_status"] = "not_logged_in"

#     if st.session_state["login_status"] == "success":
#         # st.query_params(page="main_menu")
#         # st.query_params[''] = "main_menu"
#         # # st.page_link("pages/main_menu.py")
#         # st.rerun()
#         switch_page("main_menu")
#     else:
#         main()

# col1, col2 = st.columns([1, 1])

# with col1:
#     if st.button("Submit"):
#         for user_dict in user_list:
#             if username == user_dict["username"] and password == user_dict["password"]:
#                 st.success("Login successful")
#                 st.session_state["login_status"] = "success"
#                 st.rerun()
#         st.error("Try again please")

# with col2:
#     if st.button("New Licenses"):
#         st.info("New licenses coming soon!")
############3

# if __name__ == "__main__":
#     st.set_page_config(initial_sidebar_state="collapsed")

#     if "login_status" not in st.session_state:
#         st.session_state["login_status"] = "not_logged_in"

#     if st.session_state["login_status"] == "success":
#         # st.query_params(page="main_menu")
#         # st.query_params[''] = "main_menu"
#         # # st.page_link("pages/main_menu.py")
#         # st.rerun()
#         switch_page("main_menu")
#     else:
#         main()

if __name__ == "__main__":
    st.set_page_config(initial_sidebar_state="collapsed")

    if "login_status" not in st.session_state:
        st.session_state["login_status"] = "not_logged_in"

    if st.session_state["login_status"] == "success":
        switch_page("main_menu")
    else:
        main()

