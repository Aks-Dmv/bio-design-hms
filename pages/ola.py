import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set up the connection to Google Sheets
creds_dict = st.secrets["gcp_service_account"]
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.metadata.readonly"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("BioDesign Observation Record").sheet1

# Load data from Google Sheets and convert to DataFrame
try:
    values = sheet.get_all_values()
    if not values:
        st.error("The Google Sheet appears to be empty.")
    else:
        headers = values.pop(0)  # Remove the first row as headers
        df = pd.DataFrame(values, columns=headers)
        
        # Print column names for debugging
        st.write("Column names:", df.columns.tolist())
        
        # Select Observation ID column name (adjust based on your actual column names)
        observation_id_col = "Observation ID"  # Update this to the correct name
        observation_text_col = "Observation"  # Update this to the correct name
        
        # Create a dropdown menu for selecting Observation ID
        observation_id = st.selectbox("Select an Observation ID", df[observation_id_col])
        
        # Retrieve the corresponding observation text based on the selected Observation ID
        selected_observation = df[df[observation_id_col] == observation_id][observation_text_col].values[0]
        
        # Display the selected observation
        st.write("Selected Observation:")
        st.write(selected_observation)
except KeyError as e:
    st.error(f"Column not found: {e}")
except Exception as e:
    st.error(f"An error occurred: {e}")
