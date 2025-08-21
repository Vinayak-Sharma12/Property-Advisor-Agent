from langchain_groq import ChatGroq
from langchain.chat_models import init_chat_model
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


from langchain.chat_models import init_chat_model

model = init_chat_model("open-mixtral-8x7b", model_provider="mistralai",api_key=os.getenv("MISTRAL_API_KEY"))

# print(model.invoke("hello"))