import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3-8b-8192")
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", 3))

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY no está configurada")
