from llm_client import LLMClient

llm = LLMClient()

html = "<html><body><h3>Libro A</h3><h3>Libro B</h3></body></html>"

prompt = (
    "Escribe un script en Python que use BeautifulSoup para extraer los textos "
    "de todos los <h3> del siguiente HTML y imprima una lista JSON en stdout:\n"
    + html
)

code = llm.generate_code(prompt)
print("=== CODIGO GENERADO POR LA IA ===")
print(code)
