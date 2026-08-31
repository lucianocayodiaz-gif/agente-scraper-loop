"""
scraper.py - CLI del agente: usable sin tocar código.
La salida queda como JSON versionado en outputs/ (como pide la spec).
Ejemplo:
    python scraper.py --url https://books.toscrape.com/ --schema "titulo:str,precio:float" --min 5
"""

import argparse

from main import run_scraper


def parse_schema(texto: str) -> dict:
    """'titulo:str,precio:float' -> {"titulo": "str", "precio": "float"}"""
    return dict(par.split(":") for par in texto.split(","))


def main():
    p = argparse.ArgumentParser(description="Agente scraper autonomo (Loop Engineering)")
    p.add_argument("--url", required=True, help="URL o archivo HTML a scrapear")
    p.add_argument("--schema", required=True, help='Campos y tipos: "titulo:str,precio:float"')
    p.add_argument("--min", type=int, default=1, help="Minimo de registros esperados")
    args = p.parse_args()

    data = run_scraper(args.url, parse_schema(args.schema), min_items=args.min)

    if data:
        print(f"\n✅ {len(data)} registros extraidos (JSON versionado en outputs/)")
    else:
        print("\n⛔ Sin datos en esta corrida")


if __name__ == "__main__":
    main()
