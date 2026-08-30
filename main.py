"""
main.py - Orquestador del agente scraper autónomo.
Controla el loop de 4 fases: Planificacion -> Generacion -> Ejecucion -> Validacion.
"""

import base64
import json
import os
from datetime import datetime

from bs4 import BeautifulSoup, Comment

from config import MAX_ITERATIONS
from llm_client import LLMClient
from executor import CodeExecutor
from validator import DataValidator


OUTPUT_DIR = "outputs"


def fetch_html(url: str) -> str:
    """Fase 1a: obtiene el HTML desde un archivo local o URL."""
    if url.startswith("http"):
        import urllib.request
        with urllib.request.urlopen(url, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    with open(url, encoding="utf-8") as f:
        return f.read()


def simplify_html(html: str, max_chars: int = 6000) -> str:
    """Fase 1b: mapa simplificado del DOM (sin ruido, control de tokens)."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()
    return str(soup)[:max_chars]


def build_prompt(schema: dict, dom_map: str) -> str:
    """Construye el prompt de la Fase 2 para el LLM."""
    return (
        "Eres un experto en web scraping.\n"
        "La variable `html` ya contiene el HTML de la pagina.\n"
        "Usa BeautifulSoup para extraer una lista de objetos con este esquema JSON:\n"
        f"{json.dumps(schema)}\n\n"
        "DOM simplificado de la pagina:\n"
        f"{dom_map}\n\n"
        "Devuelve UNICAMENTE codigo Python que imprima la lista JSON en stdout."
    )


def save_results(data, url: str) -> str:
    """Guarda los resultados como JSON versionado en outputs/."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"scrape_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"url": url, "data": data}, f, ensure_ascii=False, indent=2)
    return path


def run_scraper(url: str, schema: dict, seed_code: str = None):
    """Ejecuta el agente autónomo (Loop de 4 fases)."""
    print(f"🚀 Iniciando agente para: {url}")

    # Fase 1: Planificacion / Analisis del DOM
    html = fetch_html(url)
    dom_map = simplify_html(html)
    print("📊 Fase 1 completa: DOM analizado")

    llm = LLMClient()
    executor = CodeExecutor(timeout=30)
    validator = DataValidator(schema)

    prompt = build_prompt(schema, dom_map)

    # Fase 2: Generacion (o codigo sembrado para demo de auto-correccion)
    code = seed_code if seed_code else llm.generate_code(prompt)
    print("🤖 Fase 2 completa: codigo generado")

    # Inyeccion del HTML via base64 (evita problemas de escapado)
    b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
    preamble = f'import base64\nhtml = base64.b64decode("{b64}").decode("utf-8")\n'

    # Loop de Fases 3-4: Ejecucion, Validacion y Auto-correccion
    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n🔄 Iteracion {iteration}/{MAX_ITERATIONS}")

        result = executor.execute_code(preamble + code)

        if result["success"]:
            is_valid, error_msg = validator.validate(result["data"])
        else:
            is_valid, error_msg = False, result["error"]

        if is_valid:
            path = save_results(result["data"], url)
            print(f"✅ Datos validos en iteracion {iteration}")
            print(f"💾 Guardado en: {path}")
            return result["data"]

        print(f"❌ Fallo detectado: {error_msg[:200]}")

        if iteration < MAX_ITERATIONS:
            print("🔧 Auto-correccion: pidiendo fix al LLM...")
            code = llm.generate_code_with_history(prompt, code, error_msg)

    print("\n⛔ No se lograron datos validos dentro del limite de iteraciones.")
    return None


if __name__ == "__main__":
    schema = {"titulo": "str", "precio": "float"}
    run_scraper("test_sites/site_v1.html", schema)
