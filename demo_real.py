"""
demo_real.py - El agente contra un sitio real de práctica.
books.toscrape.com: catalogo con precios en libras (£).
"""

from main import run_scraper

schema = {"titulo": "str", "precio": "float"}

print("🌍 DEMO REAL: books.toscrape.com (precios con simbolo £)")
print("Umbral minimo: 5 libros\n")

data = run_scraper("https://books.toscrape.com/", schema, min_items=5, timeout=60)

if data:
    print(f"\n🏆 DEMO REAL COMPLETA: {len(data)} libros extraidos de un sitio vivo")
    for libro in data[:3]:
        print("  📖", libro)
else:
    print("\n⛔ El agente no pudo con el sitio real")
