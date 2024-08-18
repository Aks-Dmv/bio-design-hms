import streamlit as st
from streamlit_extras.switch_page_button import switch_page


from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from langchain.callbacks import get_openai_callback
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain.prompts import PromptTemplate
from langchain_pinecone import PineconeVectorStore

from add_new_observation import creds_dict

# Google Sheets setup
SCOPE = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.metadata.readonly"
        ]
CREDS = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
CLIENT = gspread.authorize(CREDS)
SPREADSHEET = CLIENT.open("BioDesign Observation Record")  # Open the main spreadsheet

def create_new_chat_sheet():
    """Create a new sheet for the current chat thread."""
    chat_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Unique name based on timestamp
    sheet = SPREADSHEET.add_worksheet(title=f"Chat_{chat_timestamp}")  # Create new sheet
    sheet.append_row(["User Input", "Assistant Response"])  # Optional: Add headers
    return sheet

# Create a new sheet for the chat thread if not already created
if "chat_sheet" not in st.session_state:
    st.session_state.chat_sheet = create_new_chat_sheet()
    
observations_csv = "observations.csv"
OPENAI_API_KEY = st.secrets["openai_key"]

st.set_page_config(page_title="Ask Observations", page_icon="❓")

st.markdown("# Ask the Team's Observations")
# st.write("This is the Ask the Team's Observations page.")
# Subtitle for the chat section

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

llm = ChatOpenAI(
    model_name="gpt-4o",
    temperature=0.7,
    openai_api_key=OPENAI_API_KEY,
    max_tokens=500,
)

db = PineconeVectorStore(
    index_name=st.secrets["pinecone-keys"]["index_to_connect"],
    namespace="observations",
    embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
    pinecone_api_key=st.secrets["pinecone-keys"]["api_key"],
)

# Handle new input
if prompt := st.chat_input("What would you like to ask?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Perform similarity search using Pinecone
    related_observations = db.similarity_search(prompt, k=10)

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
        output = observation_chat_chain.invoke({"question": prompt, "related_observations": related_observations})

    # Update the conversation history
    st.session_state.messages.append({"role": "assistant", "content": output})

    # Display the response
    with st.chat_message("assistant"):
        st.markdown(output)

    # Store chat in the current sheet
    st.session_state.chat_sheet.append_row([st.session_state.messages[-2]['content'], st.session_state.messages[-1]['content']])

st.markdown("---")
if st.button("Back to Main Menu"):
    switch_page("main_menu")
