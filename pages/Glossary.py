import streamlit as st
from streamlit_extras.switch_page_button import switch_page

import pandas as pd

st.set_page_config(page_title="Glossary", page_icon="📊")

st.markdown("# Glossary (Coming Soon)")

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set up the connection to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("path-to-your-json-file.json", scope)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("Your Google Sheet Name").sheet1  # Use .sheet1 if you're accessing the first sheet

# Retrieve all values in a specific column
# For example, to get all values in column A (the first column):
column_values = sheet.col_values(1)  # 1 represents the first column

# Display the values in the Streamlit app
st.write("Values in the selected column:")
st.write(column_values)
