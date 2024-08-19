import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd

st.set_page_config(page_title="View All Observations", page_icon="📊")

st.markdown("# All Observations")

# Embedding Google Sheets using an iframe
st.markdown("""
    <iframe src="https://docs.google.com/spreadsheets/d/1wid5imrlhkXOvmpWCbZzhAUrVSTS5iNOX3JASOxtJM4/edit?usp=sharing"
    width="200%" height="1000px"></iframe>
    """, unsafe_allow_html=True)

df = pd.read_csv("observations.csv", delimiter=';')

st.markdown("---")


# Optional: Display each observation from the CSV
# for index, row in df.iterrows():
#     st.markdown(f"### {row['observation_title']}")
#     st.markdown(f"**Date:** {row['observation_date']}")
#     st.markdown(f"**Observer:** {row['observer']}")
#     st.markdown(f"**Observation:** {row['observation']}")
#     st.markdown("---")

# import streamlit as st
# from streamlit_extras.switch_page_button import switch_page

# import pandas as pd

# st.set_page_config(page_title="View Observations Dataset", page_icon="📊")

st.markdown("# Go to the Observations Dataset")

st.markdown("""
Click the link below to open your team's observation record in Google Sheets:
<a href="https://docs.google.com/spreadsheets/d/1wid5imrlhkXOvmpWCbZzhAUrVSTS5iNOX3JASOxtJM4/edit?usp=sharing" target="_blank">Team's Observation Record</a>
""", unsafe_allow_html=True)

df = pd.read_csv("observations.csv", delimiter=';')

# st.markdown("---")

# # # Display each observation
# # for index, row in df.iterrows():
# #     st.markdown(f"### {row['observation_title']}")
# #     st.markdown(f"**Date:** {row['observation_date']}")
# #     st.markdown(f"**Observer:** {row['observer']}")
# #     st.markdown(f"**Observation:** {row['observation']}")
# #     st.markdown("---")

# # st.markdown("---")

################

# # Add custom CSS for a larger button
# st.markdown("""
#     <style>
#     div.stButton > button {
#         font-size: 60px !important;
#         padding: 20px 74px;
#         background-color: #365980; /* blueish color */
#         color: white;
#         border: none;
#         border-radius: 8px;
#         cursor: pointer;
#     }
#     div.stButton > button:hover {
#         background-color: #c2c2c2; /* Grey */
#     }
#     </style>
#     """, unsafe_allow_html=True)

# # Use Streamlit's native button for functionality
# if st.button("Back to Main Menu"):
#     switch_page("main_menu")

###############

st.markdown("---")

# Add custom CSS for a larger button
st.markdown("""
    <style>
    .big-button-container {
        display: flex;
        justify-content: center;
    }
    .big-button {
        font-size: 20px;
        padding: 10px 60px;
        background-color: #365980; /* blueish color */
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        text-align: center;
    }
    .big-button:hover {
        background-color: #c2c2c2; /* Grey */
    }
    </style>
    """, unsafe_allow_html=True)

# Create a container to hold the button with the custom class
st.markdown("""
    <div class="big-button-container">
        <button class="big-button" onclick="window.location.href='/?page=main_menu'">Back to Main Menu</button>
    </div>
    """, unsafe_allow_html=True)



# if st.button("Back to Main Menu"):
#     switch_page("main_menu")


# # Use HTML to create the bigger button
# if st.markdown('<button class="big-button">Back to Main Menu</button>', unsafe_allow_html=True):
#     switch_page("main_menu")




