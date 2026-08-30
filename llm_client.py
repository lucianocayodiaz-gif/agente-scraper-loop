from openai import OpenAI
from config import GROQ_API_KEY, LLM_MODEL

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = LLM_MODEL

    def generate_code(self, prompt: str) -> str:
        pass
