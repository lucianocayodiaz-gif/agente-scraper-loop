"""
main.py - Orquestador del agente scraper autónomo.
Loop de 4 fases + memoria + metricas + etica (robots.txt) + alertas.
"""

import base64
import json
import os
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Comment

from config import MAX_ITERATIONS
from llm_client import LLMClient
from executor import CodeExecutor
from validator import DataValidator


OUTPUT_DIR = "outputs"
METRICS_PATH = os.path.join(OUTPUT_DIR, "metrics.json")
MEMORY_PATH = os.path.join(OUTPUT_DIR, "memory.json")
ALERTAS_PATH = os.path.join(OUTPUT_DIR, "alertas.log")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AgenteScraperLoop/1.0)"}


def respetar_robots(url: str) -> bool:
    """Etica: consulta el robots.txt del sitio antes de scrapear."""
    try:
        partes = urlparse(url)
        rp = robotparser.RobotFileParser()
        rp.set_url(f"{partes.scheme}://{partes.netloc}/robots.txt")
        rp.read()
        return rp.can_fetch(HEADERS["User-Agent"], url)
    except Exception:
        return True


def registrar_alerta(url: str, mensaje: str):
    """Monitoreo: deja registro de corridas fallidas en alertas.log."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(ALERTAS_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')} | {url} | {mensaje}\n")


def fetch_html(url: str, retries: int = 3) -> str:
    """Fase 1a: obtiene HTML con User-Agent y reintentos con backoff."""
    if not url.startswith("http"):
        with open(url, encoding="utf-8") as f:
            return f.read()
    for intento in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.read().decode("utf-8", errors="ignore")
        except Exception:
            if intento == retries:
                raise
            time.sleep(2 * intento)


def page_url(url: str) -> str:
    """Convierte rutas locales a URL file:// para Playwright."""
    if url.startswith("http"):
        return url
    return Path(url).resolve().as_uri()


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
        "La variable `html` contiene el HTML inicial y `url` la URL de la pagina.\n"
        "Prefiere BeautifulSoup sobre `html` si los datos estan completos.\n"
        "Si el HTML inicial no contiene todos los datos (carga dinamica o infinite scroll), "
        "usa Playwright con `url` y haz scrolls progresivos hasta cargar todo.\n"
        "Extrae una lista de objetos con este esquema JSON:\n"
        f"{json.dumps(schema)}\n\n"
        "DOM simplificado de la pagina:\n"
        f"{dom_map}\n\n"
        "Devuelve UNICAMENTE codigo Python que imprima la lista JSON en stdout. "
        "Librerias disponibles en el sandbox: bs4, json, re, urllib, playwright.sync_api, requests."
    )


def save_results(data, url: str) -> str:
    """Guarda los resultados como JSON versionado en outputs/."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(OUTPUT_DIR, f"scrape_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"url": url, "data": data}, f, ensure_ascii=False, indent=2)
    return path


def _leer_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return default
    return default


def registrar_metrica(url, success, iterations, items, elapsed):
    """Agrega una corrida al historial de metricas (base del negocio)."""
    historial = _leer_json(METRICS_PATH, [])
    historial.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "url": url,
        "exito": success,
        "iteraciones": iterations,
        "items": items,
        "segundos": round(elapsed, 1),
    })
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)


def cargar_memoria() -> dict:
    """Memoria de selectores: {url: codigo que ya funciono}."""
    return _leer_json(MEMORY_PATH, {})


def guardar_memoria(url: str, code: str):
    mem = cargar_memoria()
    mem[url] = code
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)


def run_scraper(url, schema, seed_code=None, min_items=1, timeout=60, progress=print):
    """Ejecuta el agente autónomo (Loop + memoria + metricas + etica + alertas)."""
    inicio = time.time()
    progress(f"🚀 Iniciando agente para: {url}")

    # Etica: respetar robots.txt antes de tocar el sitio
    if url.startswith("http") and not respetar_robots(url):
        progress("🚫 Etica: el robots.txt del sitio no permite scraping. Abortando.")
        registrar_metrica(url, False, 0, 0, time.time() - inicio)
        registrar_alerta(url, "robots.txt no permite scraping")
        return None

    # Fase 1
    html = fetch_html(url)
    dom_map = simplify_html(html)
    progress("📊 Fase 1 completa: DOM analizado")

    llm = LLMClient()
    executor = CodeExecutor(timeout=timeout)
    validator = DataValidator(schema)
    prompt = build_prompt(schema, dom_map)

    # Fase 2 con prioridad: seed > memoria > LLM
    memoria = cargar_memoria()
    if seed_code:
        code = seed_code
        progress("🧪 Modo demo: codigo sembrado")
    elif url in memoria:
        code = memoria[url]
        progress("🧠 Memoria: reutilizando codigo que ya funciono en este sitio")
    else:
        code = llm.generate_code(prompt)
        progress("🤖 Fase 2 completa: codigo generado")

    b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
    preamble = (
        "import base64\n"
        f'html = base64.b64decode("{b64}").decode("utf-8")\n'
        f'url = "{page_url(url)}"\n'
    )

    # Loop Fases 3-4
    data = None
    used = 0
    for iteration in range(1, MAX_ITERATIONS + 1):
        used = iteration
        progress(f"\n🔄 Iteracion {iteration}/{MAX_ITERATIONS}")

        result = executor.execute_code(preamble + code)

        if result["success"]:
            is_valid, error_msg = validator.validate(result["data"])
            if is_valid and len(result["data"]) < min_items:
                is_valid = False
                error_msg = (
                    f"Solo se extrajeron {len(result['data'])} items y se esperan al menos {min_items}. "
                    "Posible estructura dinamica (infinite scroll). "
                    "Genera codigo con Playwright que abra `url` y haga scrolls progresivos."
                )
        else:
            is_valid, error_msg = False, result["error"]

        if is_valid:
            data = result["data"]
            path = save_results(data, url)
            guardar_memoria(url, code)
            progress(f"✅ Datos validos en iteracion {iteration}")
            progress(f"💾 Guardado en: {path}")
            break

        progress(f"❌ Fallo detectado: {error_msg[:200]}")
        if iteration < MAX_ITERATIONS:
            progress("🔧 Auto-correccion: pidiendo fix al LLM...")
            code = llm.generate_code_with_history(prompt, code, error_msg)

    registrar_metrica(url, data is not None, used, len(data) if data else 0, time.time() - inicio)

    if data is None:
        progress("\n⛔ No se lograron datos validos dentro del limite.")
        registrar_alerta(url, "loop agotado sin datos validos")
    return data


if __name__ == "__main__":
    schema = {"titulo": "str", "precio": "float"}
    run_scraper("test_sites/site_v1.html", schema)
