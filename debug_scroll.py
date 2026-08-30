"""
debug_scroll.py - Observabilidad del loop: muestra el codigo generado
y el resultado crudo del executor para diagnosticar fallos.
"""

import base64

from main import fetch_html, simplify_html, build_prompt, page_url
from llm_client import LLMClient
from executor import CodeExecutor

url = "test_sites/site_scroll.html"
schema = {"titulo": "str", "precio": "float"}

SEED_BS4 = """
import json
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")
items = []
for div in soup.find_all("div", class_="item"):
    titulo = div.find("h3", class_="title").get_text()
    precio = float(div.find("span", class_="price").get_text())
    items.append({"titulo": titulo, "precio": precio})
print(json.dumps(items))
"""

err = ("Solo se extrajeron 3 items y se esperan al menos 9. "
       "Posible estructura dinamica (infinite scroll). "
       "Genera codigo con Playwright que abra `url` y haga scrolls progresivos.")

html = fetch_html(url)
prompt = build_prompt(schema, simplify_html(html))

llm = LLMClient()
code = llm.generate_code_with_history(prompt, SEED_BS4, err)

print("===== CODIGO GENERADO (intento Playwright) =====")
print(code)
print("=================================================")

b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
preamble = (
    "import base64\n"
    f'html = base64.b64decode("{b64}").decode("utf-8")\n'
    f'url = "{page_url(url)}"\n'
)

result = CodeExecutor(timeout=60).execute_code(preamble + code)
print("success:", result["success"])
print("--- stdout crudo ---")
print(result["output"][:2000])
print("--- stderr ---")
print(result["error"][:2000])
print("--- data parseado ---")
print(result["data"])
