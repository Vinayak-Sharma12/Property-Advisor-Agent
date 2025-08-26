import streamlit as st  
import pandas as pd
import asyncio
from main import async_workflow
from langchain_community.document_loaders import CSVLoader

DATA_PATH = "dataset/Description.csv"

@st.cache_resource
def load_data():
    loader = CSVLoader(file_path=DATA_PATH, metadata_columns=["property_id"])
    docs = loader.load()
    return pd.DataFrame([{"property_id": d.metadata["property_id"], "description": d.page_content} for d in docs])

df = load_data()

@st.cache_data
def csv_load_data():
    return pd.read_csv('dataset/property_dataset_with_beautiful_description.csv')

df1=csv_load_data()

st.title("Property Agent")
query = st.text_input("Enter your query:")

if st.button("Search") and query.strip():
    with st.spinner("Processing your query..."):
        result = asyncio.run(async_workflow(query,df1))

    if isinstance(result, dict):  # property-related
        st.subheader("CSV Agent Result")
        st.write(result["csv_result"])

        st.subheader("Hybrid Search Result (Property IDs)")
        if result["hybrid_result"]:
            st.success(f"Matching IDs: {result['hybrid_result']}")
        else:
            st.warning("No properties found in hybrid search.")
    else:
        st.write(result)
