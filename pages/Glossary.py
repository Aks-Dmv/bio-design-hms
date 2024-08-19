import streamlit as st
from streamlit_extras.switch_page_button import switch_page

import pandas as pd

# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain.chains import LLMChain
# from langchain.output_parsers import PydanticOutputParser
# # from langchain.callbacks import get_openai_callback
# from langchain.schema import StrOutputParser
# from langchain.schema.runnable import RunnableLambda
# from langchain.prompts import PromptTemplate
# from langchain_pinecone import PineconeVectorStore

import gspread
from oauth2client.service_account import ServiceAccountCredentials


from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

import json
import os
import csv


st.set_page_config(page_title="Glossary", page_icon="📊")

st.markdown("# Glossary")

# If using st.secrets
creds_dict = st.secrets["gcp_service_account"]

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
st.write("New Terms:")
st.write(column_values)
