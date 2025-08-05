from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

deepseek_model = ChatGroq(
    model="deepseek-r1-distill-llama-70b",  
    api_key=os.getenv("GROQ_API_KEY")
)

llama_model=ChatGroq(
    model="llama-3.1-8b-instant",  
    api_key=os.getenv("GROQ_API_KEY")
)