import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd

st.set_page_config(page_title="View Observations Dataset", page_icon="📊")

st.markdown("# View Observations Dataset")

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

st.markdown("""
    <style>
    .big-button {
        font-size: 30px;
        padding: 20px 44px;
        background-color: #4CAF50; /* Green */
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        display: inline-block;
        margin: 10px;
    }
    .big-button:hover {
        background-color: #45a049; /* Darker green */
    }
    </style>
    """, unsafe_allow_html=True)

if st.button("Back to Main Menu"):
    switch_page("main_menu")

# if st.button("Back to Main Menu"):
#     switch_page("main_menu")


# # Use HTML to create the bigger button
# if st.markdown('<button class="big-button">Back to Main Menu</button>', unsafe_allow_html=True):
#     switch_page("main_menu")




