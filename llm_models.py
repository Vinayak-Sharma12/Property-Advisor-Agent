from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Optional import for Mistral
try:
    from langchain_mistralai import ChatMistralAI
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

load_dotenv()

def get_deepseek_model():
    """Get deepseek model with proper API key handling"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    return ChatGroq(
        model="deepseek-r1-distill-llama-70b",  
        api_key=api_key
    )

def get_llama_model():
    """Get llama model with proper API key handling"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key
    )

def get_mistral_model():
    """Get mistral model with proper API key handling"""
    if not MISTRAL_AVAILABLE:
        raise ImportError("langchain-mistralai package is not installed")
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is required")
    return ChatMistralAI(model="open-mixtral-8x7b", api_key=api_key)

# Initialize models lazily
deepseek_model = None
llama_model = None
model = None

def initialize_models():
    """Initialize all models when needed"""
    global deepseek_model, llama_model, model
    try:
        deepseek_model = get_deepseek_model()
        llama_model = get_llama_model()
        if MISTRAL_AVAILABLE and os.getenv("MISTRAL_API_KEY"):
            model = get_mistral_model()
    except Exception as e:
        print(f"Warning: Could not initialize models: {e}")
        # Set to None so the app can still run without models
        deepseek_model = None
        llama_model = None
        model = None

# print(model.invoke("hello"))