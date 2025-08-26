import os
import torch
from dotenv import load_dotenv
import streamlit as st
from pinecone import Pinecone
from pinecone_text.sparse import BM25Encoder
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import CSVLoader
from langchain_community.retrievers import PineconeHybridSearchRetriever

# ---------------------------
# Config
# ---------------------------
DATA_PATH = "dataset/Description.csv"
INDEX_NAME = "property-advisor-agent"

os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


@st.cache_resource
def load_docs():
    loader = CSVLoader(file_path=DATA_PATH, metadata_columns=["property_id"])
    return loader.load()


@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs={"device": DEVICE},
        encode_kwargs={"normalize_embeddings": True}
    )


@st.cache_resource
def load_index():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    return pc.Index(INDEX_NAME)


@st.cache_resource
def load_bm25():
    docs = load_docs()
    corpus = [d.page_content for d in docs]
    bm25 = BM25Encoder().default()
    bm25.fit(corpus)
    return bm25


@st.cache_resource
def build_retriever():
    embeddings = load_embeddings()
    bm25 = load_bm25()
    index = load_index()
    retriever = PineconeHybridSearchRetriever(
        embeddings=embeddings,
        sparse_encoder=bm25,
        index=index,
        alpha=0.5,
        top_k=10,
    )
    return retriever


# hybrid_search.py
def hybrid_search_in_property(query: str, retriever):
    results = retriever.invoke(query)

    document_text = "\n".join(
        f"Chunk {i+1}: {doc.page_content}" for i, doc in enumerate(results)
    )

    from parser_and_prompts import yes_no_prompt, yes_no_parser
    from llm_models import deepseek_model

    yes_no_model = yes_no_prompt | deepseek_model | yes_no_parser
    yes_no_result = yes_no_model.invoke({
        "user_query": query,
        "document_text": document_text
    })

    property_ids = []
    for i, answer in enumerate(yes_no_result.decisions):
        if answer == "Yes":
            property_ids.append(results[i].metadata['property_id'])

    return property_ids
