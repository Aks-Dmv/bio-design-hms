import streamlit as st
from streamlit_extras.switch_page_button import switch_page

import pandas as pd

st.set_page_config(page_title="Glossary", page_icon="📊")

st.markdown("# Glossary (Coming Soon)")

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set up the connection to Google Sheets
 scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.metadata.readonly"
        ]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
observation_sheet = client.open("BioDesign Observation Record").sheet1

# Retrieve all values in a specific column
# For example, to get all values in column A (the first column):
column_values = observation_sheet.col_values(10)  # 1 represents the first column

# Display the values in the Streamlit app
st.write("Values in the selected column:")
st.write(column_values)
