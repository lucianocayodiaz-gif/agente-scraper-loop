"""
demo_autocorreccion.py - Demo estrella del portafolio (Escenario 1 de la spec).
Simula un scraper humano escrito para v1 que se rompe cuando el sitio
cambia a v2, y muestra como el agente se auto-corrige con el Loop.
"""

from main import run_scraper

# "Scraper heredado": codigo que un humano escribio para site_v1.html
OLD_CODE = """
import json
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, "html.parser")
productos = []
for div in soup.find_all("div", class_="product"):
    titulo = div.find("h3", class_="title").get_text()
    precio = float(div.find("span", class_="price").get_text())
    productos.append({"titulo": titulo, "precio": precio})
print(json.dumps(productos))
"""

print("🎬 DEMO: el sitio cambio su estructura (v1 -> v2)")
print("El scraper heredado usa selectores viejos (.product, .title, .price)\n")

schema = {"titulo": "str", "precio": "float"}
data = run_scraper("test_sites/site_v2.html", schema, seed_code=OLD_CODE)

if data:
    print("\n🏆 DEMO COMPLETA: el agente se auto-corrigio sin intervencion humana")
    print("Datos extraidos:", data)
else:
    print("\n⛔ El agente no logro auto-corregirse")
