import os

from groq import Groq
from dotenv import load_dotenv


load_dotenv()


def create_llm():
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    return client