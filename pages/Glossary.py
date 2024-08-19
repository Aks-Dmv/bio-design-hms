import streamlit as st
from streamlit_extras.switch_page_button import switch_page

import pandas as pd

import openai

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
# from langchain.callbacks import get_openai_callback
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain.prompts import PromptTemplate
from langchain_pinecone import PineconeVectorStore

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

# # Display the values in the Streamlit app
# st.write("New Terms:")
# st.write(column_values)

# Initialize a dictionary to hold the terms and their counts
term_counts = {}

# Skip the first row (header) and process the rest
for value in column_values[1:]:
    if value:  # Check if the string is not empty
        terms = [term.strip() for term in value.split(",")]
        for term in terms:
            if term in term_counts:
                term_counts[term] += 1
            else:
                term_counts[term] = 1

# # Display the unique terms with their counts
# st.write("Unique terms and their counts:")
# for term, count in term_counts.items():
#     st.write(f"- {term} ({count})")

# Set up OpenAI API key
openai.api_key = st.secrets["openai_key"]
#openai.api_key = st.secrets["openai"]["api_key"]
#OPENAI_API_KEY = st.secrets["openai_key"]

# Function to get a definition from OpenAI
def get_definition(term):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Define the following medical term: {term}",
        max_tokens=50
    )
    definition = response.choices[0].text.strip()
    return definition

# Display the unique terms with their counts and definitions
st.write("Unique terms, their counts, and definitions:")
for term, count in term_counts.items():
    definition = get_definition(term)
    st.write(f"- **{term}** ({count}): {definition}")

