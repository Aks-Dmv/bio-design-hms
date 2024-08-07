import streamlit as st
from streamlit_extras.switch_page_button import switch_page


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

st.set_page_config(page_title="Add New Observation", page_icon="🔍")

st.markdown("# Add New Observation")


observations_csv = "observations.csv"
OPENAI_API_KEY = st.secrets["openai_key"]


if 'observation' not in st.session_state:
    st.session_state['observation'] = ""
if 'result' not in st.session_state:
    st.session_state['result'] = ""
if 'observation_summary' not in st.session_state:
    st.session_state['observation_summary'] = ""


class ObservationRecord(BaseModel):
    location: Optional[str] = Field(default=None, description="Location or setting where this observation made. e.g. operating room (OR), hospital, exam room,....")
    people_present: Optional[str] = Field(default=None, description="People present during the observation. e.g. patient, clinician, scrub tech, family member, ...")
    sensory_observations: Optional[str] = Field(default=None, description="What is the observer sensing with sight, smell, sound, touch. e.g. sights, noises, textures, scents, ...")
    specific_facts: Optional[str] = Field(default=None, description="The facts noted in the observation. e.g. the wound was 8cm, the sclera had a perforation, the patient was geriatric, ...")
    insider_language: Optional[str] = Field(default=None, description="Terminology used that is specific to this medical practice or procedure. e.g. specific words or phrases ...")
    process_actions: Optional[str] = Field(default=None, description="Which actions occurred during the observation, and when they occurred. e.g. timing of various steps of a process, including actions performed by doctors, staff, or patients, could include the steps needed to open or close a wound, ...")
    # summary_of_observation: Optional[str] = Field(default=None, description="A summary of 1 sentence of the encounter or observation, e.g. A rhinoplasty included portions that were functional (covered by insurance), and cosmetic portions which were not covered by insurance. During the surgery, the surgeon had to provide instructions to a nurse to switch between functional and cosmetic parts, back and forth. It was mentioned that coding was very complicated for this procedure, and for other procedures, because there are 3 entities in MEE coding the same procedure without speaking to each other, ...")
    questions: Optional[str] = Field(default=None, description="Recorded open questions about people or their behaviors to be investigated later. e.g. Why is this procedure performed this way?, Why is the doctor standing in this position?, Why is this specific tool used for this step of the procedure? ...")

if not os.path.exists(observations_csv):
    observation_keys = list(ObservationRecord.__fields__.keys())
    observation_keys = ['observation_summary', 'observer', 'observation', 'observation_date'] + observation_keys        
    csv_file = open(observations_csv, "w")
    csv_writer = csv.writer(csv_file, delimiter=";")
    csv_writer.writerow(observation_keys)

def parseObservation(observation: str):
    llm = ChatOpenAI(
        model_name="gpt-4o",
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

    # with get_openai_callback() as cb:
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

    # output += "\n\n"
    # output += "="*75
    # output += "\nPlease add the missing fields to the observation if needed, then proceed with adding observation to your team record."

    return f"{output}"

def addToGoogleSheets(observation_dict):
    try:
        scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.metadata.readonly"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name('awesome-nucleus-135623-eeaf5d0be309.json', scope)
        client = gspread.authorize(creds)
        observation_sheet = client.open("BioDesign Observation Record").sheet1

        headers = observation_sheet.row_values(1)

        # Prepare the row data matching the headers
        row_to_append = []
        for header in headers:
            if header in observation_dict:
                value = observation_dict[header]
                if value is None:
                    row_to_append.append("")
                else:
                    row_to_append.append(str(observation_dict[header]))
            else:
                row_to_append.append("")  # Leave cell blank if header not in dictionary

        # Append the row to the sheet
        observation_sheet.append_row(row_to_append)
        return True
    except Exception as e:
        print("Error adding to Google Sheets: ", e)
        return False

def embedObservation(observer, observation, observation_summary, observation_date):
    db = PineconeVectorStore(
            index_name=st.secrets["pinecone-keys"]["index_to_connect"],
            namespace="observations",
            embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
            pinecone_api_key=st.secrets["pinecone-keys"]["api_key"],
        )
    
    db.add_texts([observation], metadatas=[{'observer': observer}])

    parsed_observation = parseObservation(observation)

    # write observer, observatoin and parsed observation to csv
    observation_keys = list(ObservationRecord.__fields__.keys())
    all_observation_keys = ['observation_summary', 'observer', 'observation', 'observation_date'] + observation_keys
    observation_values = [observation_summary, observer, observation, observation_date] + [parsed_observation[key] for key in observation_keys]

    observation_dict = dict(zip(all_observation_keys, observation_values))
    csv_file = open(observations_csv, "a")
    csv_writer = csv.writer(csv_file, delimiter=";")
    csv_writer.writerow(observation_values)

    status = True # addToGoogleSheets(observation_dict)

    return status


def generateObservationSummary(observation):

    llm = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY,
        max_tokens=500,
    )


    observation_prompt = PromptTemplate.from_template(
"""
You help me by giving me the a one line summary of the following medical observation.

Observation: {observation}
Output:"""
)

    observation_chain = (
        observation_prompt | llm | StrOutputParser()
    )

    # with get_openai_callback() as cb:
    output = observation_chain.invoke({"observation": observation})

    return output


def clear_observation():
    st.session_state['observation'] = ""
    st.session_state['observation_summary'] = ""
    st.session_state['observation_date'] = ""
    st.session_state['result'] = ""
    st.session_state['error'] = ""

# st.session_state['observation_summary'] = st.text_input("Observation Title:", value=st.session_state['observation_summary'])

# add input called observation_id with default value of current date
observation_id_counter = 1
default_observation_id = date.today().strftime("%Y%m%d")+"%03d"%observation_id_counter
st.session_state['observation_id'] = st.text_input("Observation ID:", value=default_observation_id)

# st calendar for date input
st.session_state['observation_date'] = st.date_input("Observation Date", date.today())


# Textbox for name input
observer = st.selectbox("Observer", ["Ana", "Bridget"])

# Text area for observation input
st.session_state['observation'] = st.text_area("Add Your Observation", value=st.session_state['observation'], placeholder="Enter your observation...", height=200)

# add a voice icon button
# st.write("Voice Input")
# st.write(st.text_input("Voice Input", type="voice")
# Include Font Awesome
# st.markdown(
#     """
#     <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
#     """,
#     unsafe_allow_html=True
# )

# Button with voice icon
# button_html = """
#     <style>
#         .voice-btn {
#             border: none;
#             color: white;
#             padding: 10px 10px;
#             text-align: center;
#             text-decoration: none;
#             display: inline-block;
#             font-size: 12px;
#             margin: 1px 1px;
#             cursor: pointer;
#             border-radius: 8px; /* Add this line for rounded corners */
#         }
#     </style>
# """
    # <button class="voice-btn"><i class="fas fa-microphone"></i> Press to Speak (coming soon) </button>

# Render the button
# st.markdown(button_html, unsafe_allow_html=True)

# Container for result display
result_container = st.empty()


if st.button("Generate Observation Summary"):
    st.session_state['observation_summary']  = generateObservationSummary(st.session_state['observation'])

if st.session_state['observation_summary'] != "":
    st.session_state['observation_summary'] = st.text_area("Generated Summary (editable):", value=st.session_state['observation_summary'], height=50)


# Use columns to place buttons side by side
# col1, col2, col3 = st.columns([2, 3, 3])

# with col1:
#     if st.button("Validate Observation"):
#         st.session_state['result'] = extractObservationFeatures(st.session_state['observation'])

# with col2:
if st.button("Add Observation to Team Record"):
    # st.session_state['observation_summary']  = generateObservationSummary(st.session_state['observation'])
    st.session_state["error"] = ""

    if st.session_state['observation'] == "":
        st.session_state["error"] = "Error! Please enter observation first"
        st.markdown(
            f"<span style='color:red;'>{st.session_state['error']}</span>", 
            unsafe_allow_html=True
        )
    elif st.session_state['observation_summary'] == "":
        st.session_state["error"] = "Error! Please generate observation summary first"
        st.markdown(
            f"<span style='color:red;'>{st.session_state['error']}</span>", 
            unsafe_allow_html=True
        )
    else:
        status = embedObservation(observer, st.session_state['observation'],  st.session_state['observation_summary'], 
                            st.session_state['observation_date'])
        # st.session_state['observation_summary'] = st.text_input("Generated Summary (editable):", value=st.session_state['observation_summary'])
        # "Generated Summary: "+st.session_state['observation_summary']+"\n\n"
        if status:
            st.session_state['result'] = "Observation added to your team's database"
        else:
            st.session_state['result'] = "Error adding observation to your team's database, try again!"
        # clear_observation()

st.write(f"{st.session_state['result']}")

st.markdown("---")

if st.button("Back to Main Menu"):
    clear_observation()
    switch_page("main_menu")
