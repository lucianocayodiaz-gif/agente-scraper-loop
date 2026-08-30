"""
demo_infinite_scroll.py - Escenario 2 de la spec.
La pagina carga mas items al hacer scroll. El agente detecta el volumen
bajo y genera una rutina Playwright de scrolls progresivos.
"""

from main import run_scraper

# Scraper estatico sembrado: solo ve los 3 items iniciales del HTML
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

print("🎬 DEMO: pagina con infinite scroll (3 items visibles, 9 totales)")
print("Umbral minimo: 9 items\n")

schema = {"titulo": "str", "precio": "float"}
data = run_scraper("test_sites/site_scroll.html", schema, seed_code=SEED_BS4, min_items=9, timeout=60)

if data:
    print(f"\n🏆 DEMO COMPLETA: {len(data)} items extraidos tras auto-correccion con Playwright")
else:
    print("\n⛔ El agente no logro completar el infinite scroll")
