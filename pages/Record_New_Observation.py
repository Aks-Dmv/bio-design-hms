import time
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
from datetime import date, datetime

import json
import os
import csv

st.set_page_config(page_title="Add a New Observation", page_icon="🔍")

st.markdown("# Add a New Observation")


observations_csv = "observations.csv"
OPENAI_API_KEY = st.secrets["openai_key"]

# Access the credentials from Streamlit secrets
#test
creds_dict = {
    "type" : st.secrets["gcp_service_account"]["type"],
    "project_id" : st.secrets["gcp_service_account"]["project_id"],
    "private_key_id" : st.secrets["gcp_service_account"]["private_key_id"],
    "private_key" : st.secrets["gcp_service_account"]["private_key"],
    "client_email" : st.secrets["gcp_service_account"]["client_email"],
    "client_id" : st.secrets["gcp_service_account"]["client_id"],
    "auth_uri" : st.secrets["gcp_service_account"]["auth_uri"],
    "token_uri" : st.secrets["gcp_service_account"]["token_uri"],
    "auth_provider_x509_cert_url" : st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url" : st.secrets["gcp_service_account"]["client_x509_cert_url"],
    "universe_domain": st.secrets["gcp_service_account"]["universe_domain"],
}


if 'observation' not in st.session_state:
    st.session_state['observation'] = ""

if 'result' not in st.session_state:
    st.session_state['result'] = ""

if 'observation_summary' not in st.session_state:
    st.session_state['observation_summary'] = ""

if 'observation_date' not in st.session_state:
    st.session_state['observation_date'] = date.today()

if 'rerun' not in st.session_state:
    st.session_state['rerun'] = False

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
    observation_keys = ['observation_summary', 'observer', 'observation', 'observation_date', 'observation_id'] + observation_keys        
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
    # for field in missing_fields:
    #     output += f" {field},"

    # # output += "\n\n"
    # # output += "="*75
    # output += "\nPlease add the missing fields to the observation if needed, then proceed with adding observation to your team record."

    # return f"{output}"

     # Add each missing field in red
    for field in missing_fields:
        output += f" <span style='color:red;'>{field}</span>,"

    # Display the output
    # st.markdown(output, unsafe_allow_html=True)
    return f"{output}"

def addToGoogleSheets(observation_dict):
    try:
        scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.metadata.readonly"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
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

def embedObservation(observer, observation, observation_summary, observation_date, observation_id):
    db = PineconeVectorStore(
            index_name=st.secrets["pinecone-keys"]["index_to_connect"],
            namespace="observations",
            embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
            pinecone_api_key=st.secrets["pinecone-keys"]["api_key"],
        )
    
    db.add_texts([observation], metadatas=[{'observer': observer, 'observation_date': observation_date, 'observation_id': observation_id}])

    parsed_observation = parseObservation(observation)

    # write observer, observatoin and parsed observation to csv
    observation_keys = list(ObservationRecord.__fields__.keys())
    all_observation_keys = ['observation_summary', 'observer', 'observation', 'observation_date', 'observation_id'] + observation_keys
    observation_values = [observation_summary, observer, observation, observation_date, observation_id] + [parsed_observation[key] for key in observation_keys]

    observation_dict = dict(zip(all_observation_keys, observation_values))
    csv_file = open(observations_csv, "a")
    csv_writer = csv.writer(csv_file, delimiter=";")
    csv_writer.writerow(observation_values)

    status = addToGoogleSheets(observation_dict)

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
Output Summary:"""
)

    observation_chain = (
        observation_prompt | llm | StrOutputParser()
    )

    # with get_openai_callback() as cb:
    output = observation_chain.invoke({"observation": observation})

    return output


def clear_observation():
    if 'observation' in st.session_state:
        st.session_state['observation'] = ""
    if 'observation_summary' in st.session_state:
        st.session_state['observation_summary'] = ""
    if 'result' in st.session_state:
        st.session_state['result'] = ""
    update_observation_id()

import streamlit as st
from datetime import date

# Initialize or retrieve the observation counters dictionary from session state
if 'observation_counters' not in st.session_state:
    st.session_state['observation_counters'] = {}

# Function to generate observation ID with the format OBYYMMDDxxxx
def generate_observation_id(observation_date, counter):
    return f"OB{observation_date.strftime('%y%m%d')}{counter:04d}"

# Function to update observation ID when the date changes
def update_observation_id():
    obs_date_str = st.session_state['observation_date'].strftime('%y%m%d')

    # get all observation ids from the sheets and update the counter
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.metadata.readonly"
        ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    observation_sheet = client.open("BioDesign Observation Record").sheet1
    column_values = observation_sheet.col_values(1) 

    # find all observation ids with the same date
    obs_date_ids = [obs_id for obs_id in column_values if obs_id.startswith(f"OB{obs_date_str}")]
    obs_date_ids.sort()

    # get the counter from the last observation id
    if len(obs_date_ids) > 0:
        counter = int(obs_date_ids[-1][-4:])+1
    else:
        counter = 1
    
    # # Check if the date is already in the dictionary
    # if obs_date_str in st.session_state['observation_counters']:
    #     # Increment the counter for this date
    #     st.session_state['observation_counters'][obs_date_str] += 1
    # else:
    #     # Initialize the counter to 1 for a new date
    #     st.session_state['observation_counters'][obs_date_str] = 1
    
    # Generate the observation ID using the updated counter
    # counter = st.session_state['observation_counters'][obs_date_str]

    st.session_state['observation_id'] = generate_observation_id(st.session_state['observation_date'], counter)

# Use columns to place observation_date, observation_id, and observer side by side
col1, col2, col3 = st.columns(3)

with col1:
    # st calendar for date input with a callback to update the observation_id
    st.date_input("Observation Date", date.today(), on_change=update_observation_id, key="observation_date")

with col2:
    # Ensure the observation ID is set the first time the script runs
    if 'observation_id' not in st.session_state:
        update_observation_id()

    # Display the observation ID
    st.text_input("Observation ID:", value=st.session_state['observation_id'], disabled=True)

with col3:
    #Display Observer options 
    observer = st.selectbox("Observer", ["Ana", "Bridget"])

############

# # Function to generate observation ID with the format OBYYYYMMDDxxxx
# def generate_observation_id(observation_date, counter):
#     return f"OB{observation_date.strftime('%y%m%d')}{counter:04d}"

# # Initialize or retrieve observation ID counter from session state
# if 'observation_id_counter' not in st.session_state:
#     st.session_state['observation_id_counter'] = 1

# # Function to update observation ID when the date changes
# def update_observation_id():
#     st.session_state['observation_id'] = generate_observation_id(st.session_state['observation_date'], st.session_state['observation_id_counter'])

# # st calendar for date input with a callback to update the observation_id
# st.session_state['observation_date'] = st.date_input("Observation Date", date.today(), on_change=update_observation_id)

# # Initialize observation_id based on the observation date and counter
# st.session_state['observation_id'] = st.text_input("Observation ID:", value=st.session_state['observation_id'], disabled=True)

##########

#new_observation_id = st.observation_date().strftime("%Y%m%d")+"%03d"%observation_id_counter
#st.session_state['observation_id'] = st.text_input("Observation ID:", value=new_observation_id)

#########

# Textbox for name input
#observer = st.selectbox("Observer", ["Ana", "Bridget"])

# ######

# # Text area for observation input
# st.session_state['observation'] = st.text_area("Add Your Observation", value=st.session_state['observation'], placeholder="Enter your observation...", height=200)

# ######


# Initialize the observation text in session state if it doesn't exist
if "observation" not in st.session_state:
    st.session_state["observation"] = ""

# Function to clear the text area
def clear_text():
    st.session_state["observation"] = ""

#st.markdown("---")

# Observation Text Area
##

#observation_text = st.text_area("Observation", value=st.session_state["observation"], height=200, key="observation")

# Add Your Observation Text with larger font size
st.markdown("<h4 style='font-size:20px;'>Add Your Observation:</h4>", unsafe_allow_html=True)

# Button for voice input (currently as a placeholder)
if st.button("🎤 Record Observation (Coming Soon)"):
    st.info("Voice recording feature coming soon!")

# Observation Text Area
st.session_state['observation'] = st.text_area("Observation:", value=st.session_state["observation"], height=200)


# Create columns to align the buttons
col1, col2, col3 = st.columns([2, 2, 2])  # Adjust column widths as needed

with col3:
    # Use custom CSS for the red button
    # st.markdown("""
    #     <style>
    #     .stButton > button {
    #         background-color: #942124;
    #         color: white;
    #         font-size: 16px;
    #         padding: 10px 20px;
    #         border-radius: 8px;
    #         border: none;
    #     }
    #     .stButton > button:hover {
    #         background-color: darkred;
    #     }
    #     </style>
    #     """, unsafe_allow_html=True)

    # Button to Clear the Observation Text Area
    st.button("Clear Observation", on_click=clear_text)
    
    # Container for result display
    result_container = st.empty()

# #Use columns to place buttons side by side
# col11, col21 = st.columns(2)


# with col11:
#     if st.button("Generate Observation Summary"):
#         st.session_state['observation_summary']  = generateObservationSummary(st.session_state['observation'])

#     if st.session_state['observation_summary'] != "":
#         st.session_state['observation_summary'] = st.text_area("Generated Summary (editable):", value=st.session_state['observation_summary'], height=50)
    

with col1:
    if st.button("Evaluate Observation"):
        st.session_state['result'] = extractObservationFeatures(st.session_state['observation'])
        st.session_state['observation_summary']  = generateObservationSummary(st.session_state['observation'])
    
if st.session_state['observation_summary'] != "":
    st.session_state['observation_summary'] = st.text_area("Generated Summary (editable):", value=st.session_state['observation_summary'], height=50)

# st.write(f":green[{st.session_state['result']}]")
st.markdown(st.session_state['result'], unsafe_allow_html=True)

if st.session_state['rerun']:
    time.sleep(3)
    clear_observation()
    st.session_state['rerun'] = False
    st.rerun()
    
    ##########

if st.button("Add Observation to Team Record", disabled=st.session_state['observation_summary'] == ""):
    # st.session_state['observation_summary']  = generateObservationSummary(st.session_state['observation'])
    st.session_state["error"] = ""

    if st.session_state['observation'] == "":
        st.session_state["error"] = "Error! Please enter observation first"
        st.markdown(
            f"<span style='color:red;'>{st.session_state['error']}</span>", 
            unsafe_allow_html=True
        )
    elif st.session_state['observation_summary'] == "":
        st.session_state["error"] = "Error! Please evaluate observation first"
        st.markdown(
            f"<span style='color:red;'>{st.session_state['error']}</span>", 
            unsafe_allow_html=True
        )
    else:
        status = embedObservation(observer, st.session_state['observation'],  st.session_state['observation_summary'], 
                            st.session_state['observation_date'],
                            st.session_state['observation_id'])
        # st.session_state['observation_summary'] = st.text_input("Generated Summary (editable):", value=st.session_state['observation_summary'])
        # "Generated Summary: "+st.session_state['observation_summary']+"\n\n"
        if status:
            st.session_state['result'] = "Observation added to your team's database."
            st.session_state['rerun'] = True
            st.rerun()
        else:
            st.session_state['result'] = "Error adding observation to your team's database, try again!"
        # clear_observation()

st.markdown("---")

# if st.button("Back to Main Menu"):
#     clear_observation()
#     switch_page("main_menu")


# st.markdown("---")
# Apply custom CSS to make the button blue
st.markdown("""
    <style>
    div.stButton > button {
        background-color: #365980;
        color: white;
        font-size: 16px;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
    }
    div.stButton > button:hover {
        background-color: #2c4a70;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)



# Create a button using Streamlit's native functionality
if st.button("Back to Main Menu"):
    switch_page("main_menu")
