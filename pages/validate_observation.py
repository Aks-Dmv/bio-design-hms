import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Learn From Observations", page_icon="✅")
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd


from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from langchain.callbacks import get_openai_callback
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableLambda
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import OpenAIEmbeddings

OPENAI_API_KEY = st.secrets["openai_key"]

st.markdown("# Learn From Observations")

df = pd.read_csv("observations.csv", delimiter=';')

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
What other things could have caused or contibuted to this problem?
What could have been done to avoid the problem?
What other problems exist because this problem exists?
Stakeholder definition:
Specific description of who specifically had this problem (Man, Woman, Child, Age, Socio-economic background, etc.)A
re there any other populations that would have this problem? (all OR patients, all patients over 65, all patients with CF, etc.)
Are there any populations that experience the same problem with more severity than what was observed?
Are there any populations that experience the same problem with less severity than what was observed?
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

    observation_chain = (
        observation_prompt | llm | StrOutputParser()
    )

    with get_openai_callback() as cb:
        output = observation_chain.invoke({"observation": observation, "questions_list": questions_list})

    return output

# Display each observation
for index, row in df.iterrows():
    st.markdown(f"### {row['observation_title']}")
    st.markdown(f"**Date:** {row['observation_date']}")
    st.markdown(f"**Observer:** {row['observer']}")
    st.markdown(f"**Observation:** {row['observation']}")
    
    if st.button(f"Get Tips for this Observation", key=f"tips_button_{index}"):
        tips = get_tips_from_observation(row['observation'])
        st.markdown(tips)
    
    st.markdown("---")

st.markdown("---")

if st.button("Back to Main Menu"):
    switch_page("main_menu")
