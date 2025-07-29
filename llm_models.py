from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llama_model = ChatGroq(
    model="deepseek-r1-distill-llama-70b",  
    api_key=os.getenv("GROQ_API_KEY")
)
