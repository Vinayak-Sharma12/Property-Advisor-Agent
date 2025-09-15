import os
from langchain_community.document_loaders import CSVLoader
from dotenv import load_dotenv
from pinecone import Pinecone,ServerlessSpec
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.retrievers import PineconeHybridSearchRetriever
from pinecone_text.sparse import BM25Encoder
load_dotenv()

import torch
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(device)

#Load CSV
loader = CSVLoader(file_path="/Users/slimshady/Documents/Property Advisor /Property-Advisor-Agent/dataset/Real_Description.csv",metadata_columns=['property_id'])
docs = loader.load()
# print(docs[0])

#CREATE PINECONE CLIENT 
pc=Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

#CREATE INDEX 
index_name="property-advisor-agent"
if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1024,  # dimensionality of dense model
            metric="dotproduct",  # sparse values supported only for dotproduct
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
index = pc.Index(index_name)

#Embeddings 
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-en-v1.5",
    model_kwargs={"device": device},
    encode_kwargs={"normalize_embeddings": True}
        )

#BM25-ENCODER 
bm25_encoder = BM25Encoder().default()
corpus = [d.page_content for d in docs]
bm25_encoder.fit(corpus)


#Setting Up Retriever
texts = [d.page_content for d in docs]
metadatas = [d.metadata for d in docs]
retriever=PineconeHybridSearchRetriever(embeddings=embeddings,sparse_encoder=bm25_encoder,index=index,alpha=0.5,top_k=40)
retriever.add_texts(texts=texts,metadatas=metadatas)
print("Documents add to Retriever")