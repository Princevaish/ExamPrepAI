import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    temperature=0.7,
    max_tokens=None,
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile"
)

llm2 = ChatGroq(
    temperature=0.7,
    max_tokens=None,
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile"
)
llm3= ChatGroq(
    temperature=0.7,
    max_tokens=None,
    groq_api_key=groq_api_key,
    model_name="llama-3.1-8b-instant"
)