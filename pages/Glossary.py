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
observation_ids = observation_sheet.col_values(1)  # 1 represents the first column

# # Display the values in the Streamlit app
# st.write("New Terms:")
# st.write(column_values)

# Initialize a dictionary to hold the terms and their counts
term_counts = {}
relevant_observation_ids = {}

# Skip the first row (header) and process the rest
for i, value in enumerate(column_values[1:]):
    if value:  # Check if the string is not empty
        terms = [term.strip() for term in value.split(",")]
        for term in terms:
            if term in term_counts:
                term_counts[term] += 1
                relevant_observation_ids[term].append(observation_ids[i+1])
            else:
                term_counts[term] = 1
                relevant_observation_ids[term] = [observation_ids[i+1]]

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
    openai_client = openai.OpenAI(api_key=openai.api_key)
    
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that provides concise definitions of medical terms."},
            {"role": "user", "content": f"Define the following medical term: {term}"}
        ]
        response = openai_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
        )
        definition = response.choices[0].message.content
    
        return definition
    except Exception as e:
        return f"Error: {e}"

# Display the unique terms with their counts and definitions
st.write("Unique terms, their counts, and definitions:")

# Sort the terms alphabetically
sorted_terms = sorted(term_counts.keys())

for term in sorted_terms:
    capitalized_term = term.capitalize()
    definition = get_definition(term)
    st.markdown(f"""
- **{capitalized_term}** ({term_counts[capitalized_term]}): {definition}  
_Relevant observation IDs:_ {relevant_observation_ids[capitalized_term]}
""")

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


