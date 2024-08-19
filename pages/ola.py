import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import StrOutputParser
from langchain.callbacks import get_openai_callback
from langchain.prompts import PromptTemplate

# Set up the connection to Google Sheets
creds_dict = st.secrets["gcp_service_account"]
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.metadata.readonly"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("BioDesign Observation Record").sheet1

# Set up the OpenAI API key
OPENAI_API_KEY = st.secrets["openai_key"]

st.set_page_config(page_title="Tips for Observations", page_icon="✅")
st.markdown("# Tips for Observations")

# Load data from Google Sheets and convert to DataFrame
try:
    values = sheet.get_all_values()
    if not values:
        st.error("The Google Sheet appears to be empty.")
    else:
        headers = values.pop(0)  # Remove the first row as headers
        df = pd.DataFrame(values, columns=headers)
        
        # Select only columns 1 (Observation ID) and 5 (Observation text)
        df_selected = df.iloc[:, [0, 4]]  # This selects columns 1 (Observation ID) and 5 (Observation)
        st.write(df_selected)  # Display the selected columns
        
        # Create a dropdown menu for selecting Observation ID
        observation_id = st.selectbox("Select an Observation ID", df_selected['Observation ID'])
        
        # Get the observation text based on the selected Observation ID
        selected_observation = df_selected[df_selected['Observation ID'] == observation_id]['Observation'].values[0]
        
except Exception as e:
    st.error(f"An error occurred: {e}")

def get_tips_from_observation(observation):
    llm = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY,
        max_tokens=500,
    )

    questions_list = """
    Problem definition:
    What was the stated or principle cause of the problem you observed?
    What other things could have caused or contributed to this problem?
    What could have been done to avoid the problem?
    What other problems exist because this problem exists?
    Stakeholder definition:
    Specific description of who specifically had this problem (Man, Woman, Child, Age, Socio-economic background, etc.)
    Are there any other populations that would have this problem? (all OR patients, all patients over 65, all patients with CF, etc.)
    Are there any populations that experience the same problem with more severity than what was observed?
    Are there any populations that experience the same problem with less severity than what was observed?
    Outcome definition:
    What is the desired outcome with current treatments?
    What is the ideal outcome desired to lessen the problem to a manageable amount?
    What is the desired outcome to eliminate the problem?
    What is the outcome if you prevented the problem?
    """

    observation_prompt = PromptTemplate.from_template(
        """
        You help me by giving me the most relevant two questions from the list that have not been answered in the following observation.
        The observation is about a medical procedure and the questions are about the problem, stakeholders, and outcomes.
        The answers should not be present but the chosen two questions must be very relevant to the observation.
        Be concise in your output, and give a maximum of the two questions!

        List of questions: {questions_list}

        Observation: {observation}
        Output:"""
    )

    observation_chain = LLMChain(
        prompt=observation_prompt,
        llm=llm,
        output_parser=StrOutputParser()
    )

    with get_openai_callback() as cb:
        output = observation_chain.run({"observation": observation, "questions_list": questions_list})

    return output

# Display tips for the selected observation
if st.button("Get Tips"):
    tips = get_tips_from_observation(selected_observation)
    st.markdown(tips)

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

