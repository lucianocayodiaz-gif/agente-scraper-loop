from config import MAX_ITERATIONS
from llm_client import LLMClient
from executor import CodeExecutor
from validator import DataValidator

def run_scraper(url: str, schema: dict):
    print(f"Iniciando agente scraper para: {url}")
    
    llm = LLMClient()
    executor = CodeExecutor()
    validator = DataValidator(schema)
    
    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"Iteración {iteration}/{MAX_ITERATIONS}")
    
    print("Agente completado")

if __name__ == "__main__":
    run_scraper("https://example.com", {"titulo": "str"})
