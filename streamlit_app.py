import streamlit as st

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from langchain.callbacks import get_openai_callback
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

import json
import os
import csv

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_name('awesome-nucleus-135623-eeaf5d0be309.json', scope)
# client = gspread.authorize(creds)
# sheet = client.open("BioDesign Observation Record").sheet1


observations_csv = "observations.csv"
OPENAI_API_KEY = st.secrets["openai_key"]


if 'observation' not in st.session_state:
    st.session_state['observation'] = ""
if 'result' not in st.session_state:
    st.session_state['result'] = ""
if 'observation_title' not in st.session_state:
    st.session_state['observation_title'] = ""


class ObservationRecord(BaseModel):
    date: Optional[str] = Field(default=None, description="Date of the observation")
    location: Optional[str] = Field(default=None, description="Location or setting where this observation made. e.g. operating room (OR), hospital, exam room,....")
    people_present: Optional[str] = Field(default=None, description="People present during the observation. e.g. patient, clinician, scrub tech, family member, ...")
    sensory_observations: Optional[str] = Field(default=None, description="What is the observer sensing with sight, smell, sound, touch. e.g. sights, noises, textures, scents, ...")
    specific_facts: Optional[str] = Field(default=None, description="The facts noted in the observation. e.g. the wound was 8cm, the sclera had a perforation, the patient was geriatric, ...")
    insider_language: Optional[str] = Field(default=None, description="Terminology used that is specific to this medical practice or procedure. e.g. specific words or phrases ...")
    process_actions: Optional[str] = Field(default=None, description="Which actions occurred during the observation, and when they occurred. e.g. timing of various steps of a process, including actions performed by doctors, staff, or patients, could include the steps needed to open or close a wound, ...")
    summary_of_observation: Optional[str] = Field(default=None, description="A summary of 3-5 sentences of the encounter or observation, e.g. A rhinoplasty included portions that were functional (covered by insurance), and cosmetic portions which were not covered by insurance. During the surgery, the surgeon had to provide instructions to a nurse to switch between functional and cosmetic parts, back and forth. It was mentioned that coding was very complicated for this procedure, and for other procedures, because there are 3 entities in MEE coding the same procedure without speaking to each other, ...")
    questions: Optional[str] = Field(default=None, description="Recorded open questions about people or their behaviors to be investigated later. e.g. Why is this procedure performed this way?, Why is the doctor standing in this position?, Why is this specific tool used for this step of the procedure? ...")

if not os.path.exists(observations_csv):
        observation_keys = list(ObservationRecord.__fields__.keys())
        observation_keys = ['observer', 'observation'] + observation_keys        
        csv_file = open(observations_csv, "w")
        csv_writer = csv.writer(csv_file, delimiter=";")
        csv_writer.writerow(observation_keys)

def parseObservation(observation: str):
    llm = ChatOpenAI(
        model_name="gpt-4-1106-preview",
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY,
        max_tokens=500,
    )

    observation_prompt = PromptTemplate.from_template(
"""
You help me parse observations of medical procedures to extract details such as  surgeon, procedure and date, whichever is available.
Format Instructions for output: {format_instructions}

Observation: {observation}
Output:"""
)
    observationParser = PydanticOutputParser(pydantic_object=ObservationRecord)
    observation_format_instructions = observationParser.get_format_instructions()

    observation_chain = (
        observation_prompt | llm | observationParser
    )

    with get_openai_callback() as cb:
        output = observation_chain.invoke({"observation": observation, "format_instructions": observation_format_instructions})

    return json.loads(output.json())

def extractObservationFeatures(observation):

    # Parse the observation
    parsed_observation = parseObservation(observation)

    input_fields = list(ObservationRecord.__fields__.keys())

    missing_fields = [field for field in input_fields if parsed_observation[field] is None]

    output = ""

    for field in input_fields:
        if field not in missing_fields:
            key_output = field.replace("_", " ").capitalize()
            output += f"**{key_output}**: {parsed_observation[field]}\n"
            output += "\n"

    missing_fields = [field.replace("_", " ").capitalize() for field in missing_fields]

    output += "\n\n **Missing fields**:"
    for field in missing_fields:
        output += f" {field},"

    output += "\n\n"
    output += "="*75
    output += "\nPlease add the missing fields to the observation if needed, then proceed with adding observation to your team record."

    return f"{output}"

def embedObservation(observer, observation):
    db = Chroma(
            collection_name="observations",
            embedding_function=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
            persist_directory="db"
        )
    
    db.add_texts([observation], metadatas=[{'observer': observer}])

    parsed_observation = parseObservation(observation)

    # write observer, observatoin and parsed observation to csv
    observation_keys = list(ObservationRecord.__fields__.keys())
    observation_values = [observer, observation] + [parsed_observation[key] for key in observation_keys]
    csv_file = open(observations_csv, "a")
    csv_writer = csv.writer(csv_file, delimiter=";")
    csv_writer.writerow(observation_values)

    print("Observation embedded to the database")

def clear_observation():
    st.session_state['observation'] = ""
    st.session_state['observation_title'] = ""

def askObservations(question):
    llm = ChatOpenAI(
        model_name="gpt-4-1106-preview",
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY,
        max_tokens=500,
    )

    db = Chroma(
                collection_name="observations",
                embedding_function=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
                persist_directory="db"
            )
    
    related_observations = db.similarity_search(question, k=10)

    print("Related observations: ", related_observations)

    question_prompt = PromptTemplate.from_template(
"""
You are a helpful assistant trained in the Stanford biodesign process that can answer questions about observations of medical procedures. You can use the related observations to help answer the question.

Question: {question}
Related Observations: {related_observations}
"""
)
    
    observation_chat_chain = (
        question_prompt | llm | StrOutputParser()
    )

    with get_openai_callback() as cb:
        output = observation_chat_chain.invoke({"question": question, "related_observations": related_observations})
        # print(cb)

    print(output)

    return output


# Title for the application
st.title("BioDesign Copilot")
st.subheader("Observation Assistant")

st.session_state['observation_title'] = st.text_input("Observation Title:", value=st.session_state['observation_title'])

# st calendar for date input
st.date_input("Observation Date", date.today())


# Textbox for name input
observer = st.selectbox("Observer", ["Bridget", "Ana"])

# Text area for observation input
st.session_state['observation'] = st.text_area("Add Your Observation", value=st.session_state['observation'], placeholder="Enter your observation...", height=200)

# add a voice icon button
# st.write("Voice Input")
# st.write(st.text_input("Voice Input", type="voice")
# Include Font Awesome
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
    """,
    unsafe_allow_html=True
)

# Button with voice icon
button_html = """
    <style>
        .voice-btn {
            border: none;
            color: white;
            padding: 10px 10px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 12px;
            margin: 1px 1px;
            cursor: pointer;
            border-radius: 8px; /* Add this line for rounded corners */
        }
    </style>
    <button class="voice-btn"><i class="fas fa-microphone"></i> Press to Speak (coming soon) </button>
"""

# Render the button
st.markdown(button_html, unsafe_allow_html=True)

# Container for result display
result_container = st.empty()

# Use columns to place buttons side by side
col1, col2 = st.columns([1, 3])

with col1:
    if st.button("Validate Observation"):
        st.session_state['result'] = extractObservationFeatures(st.session_state['observation'])

with col2:
    if st.button("Add Observation to Team Record"):
        embedObservation(observer, st.session_state['observation'])
        st.session_state['result'] = "Observation added to your team's database"
        clear_observation()
        st.experimental_rerun()

# if st.button("Remove Redundancies \n (Coming Soon)"):
#     st.session_state['observation'] = st.session_state['observation']

st.write(f"{st.session_state['result']}")


# # Display the result outside the columns to ensure it appears below them
# # This avoids the result being overwritten by column content
# if 'result' in st.session_state:
#     result_container.write(f"{st.session_state['result']}")


# # Button to add observation
# if st.button("Validate Observation"):
#     st.session_state['result'] = extractObservationFeatures(st.session_state['observation'])
    

# # Display the result

# st.write(f"{st.session_state['result']}")


# if st.button("Add Observation to Team Record"):
#     embedObservation(observer, st.session_state['observation'])
#     st.write("Observation added to your team's database")
#     clear_observation()
#     st.experimental_rerun()

st.markdown("---")

# if st.button("Open Team's Observation Record (Coming Soon)"):
#     # open https://docs.google.com/spreadsheets/d/1wid5imrlhkXOvmpWCbZzhAUrVSTS5iNOX3JASOxtJM4/edit?usp=sharing in new tab
#     js = "window.open('https://docs.google.com/spreadsheets/d/1wid5imrlhkXOvmpWCbZzhAUrVSTS5iNOX3JASOxtJM4/edit?usp=sharing')"
#     html = '<img src onerror="{}">'.format(js)
#     div = st.markdown(html, unsafe_allow_html=True)


st.markdown("""

Click the link below to open your team's observation record in Google Sheets:

<a href="https://docs.google.com/spreadsheets/d/1wid5imrlhkXOvmpWCbZzhAUrVSTS5iNOX3JASOxtJM4/edit?usp=sharing" target="_blank">Team's Observation Record</a>
""", unsafe_allow_html=True)

# Divider
st.markdown("---")

# Subtitle for the chat section
st.subheader("Chat with your team's observations")

# Textbox for asking questions
question = st.text_input("Ask a question:", key="question")

# Button to ask questions
if st.button("Ask", key="ask"):
    # Call the askObservations function and store the result
    answer = askObservations(question)
    
    # Display the result
    st.write(f"**Copilot says:** {answer}")
