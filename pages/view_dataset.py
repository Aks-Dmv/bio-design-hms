import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd

st.set_page_config(page_title="View Observations Dataset", page_icon="📊")

st.markdown("# View Observations Dataset")

# Embedding Google Sheets using an iframe
st.markdown("""
    <iframe src="https://docs.google.com/spreadsheets/d/1wid5imrlhkXOvmpWCbZzhAUrVSTS5iNOX3JASOxtJM4/edit?usp=sharing"
    width="400%" height="1000px"></iframe>
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

if st.button("Back to Main Menu"):
    switch_page("main_menu")


# import streamlit as st
# from streamlit_extras.switch_page_button import switch_page

# import pandas as pd

# st.set_page_config(page_title="View Observations Dataset", page_icon="📊")

# st.markdown("# View Observations Dataset")

# st.markdown("""

# Click the link below to open your team's observation record in Google Sheets:

# <a href="https://docs.google.com/spreadsheets/d/1wid5imrlhkXOvmpWCbZzhAUrVSTS5iNOX3JASOxtJM4/edit?usp=sharing" target="_blank">Team's Observation Record</a>
# """, unsafe_allow_html=True)

# df = pd.read_csv("observations.csv", delimiter=';')

# st.markdown("---")

# # # Display each observation
# # for index, row in df.iterrows():
# #     st.markdown(f"### {row['observation_title']}")
# #     st.markdown(f"**Date:** {row['observation_date']}")
# #     st.markdown(f"**Observer:** {row['observer']}")
# #     st.markdown(f"**Observation:** {row['observation']}")
# #     st.markdown("---")

# # st.markdown("---")

# if st.button("Back to Main Menu"):
#     switch_page("main_menu")
