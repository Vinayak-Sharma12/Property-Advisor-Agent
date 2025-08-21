import streamlit as st  
import pandas as pd
import asyncio
from main import async_workflow

@st.cache_data
def load_data():
    return pd.read_csv('dataset/property_dataset_with_beautiful_description.csv')

df = load_data()

st.title("Property Agent")
user_input = st.text_input("Enter your query:")

if st.button("Submit"):
    result = asyncio.run(async_workflow(user_input, df))  # Await the async workflow
    if result is None:
        st.write("Alright! Tell me Your Requirements")
    else:
        st.write(result)
    st.success("Processed successfully!")