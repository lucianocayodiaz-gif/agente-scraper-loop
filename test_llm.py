from openai import OpenAI
from config import GROQ_API_KEY, LLM_MODEL

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
resp = client.chat.completions.create(
    model=LLM_MODEL,
    messages=[{"role": "user", "content": "Responde exactamente: CONEXION OK"}],
)
print("Respuesta del LLM:", resp.choices[0].message.content)
