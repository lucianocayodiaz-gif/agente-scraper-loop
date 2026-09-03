"""Comparador multi-supermercado: corre el agente contra varias URLs
y acumula los precios en un solo JSON, etiquetados por tienda."""
import argparse
import json
import os
from datetime import datetime
from urllib.parse import urlparse

from main import run_scraper


def parse_schema(texto):
    """Convierte 'titulo:str,precio:float' en un diccionario."""
    schema = {}
    for par in texto.split(","):
        campo, tipo = par.split(":")
        schema[campo.strip()] = tipo.strip()
    return schema


def main():
    p = argparse.ArgumentParser(description="Comparador de precios multi-sitio")
    p.add_argument("--urls", nargs="+", required=True,
                   help="Las URLs en fila, separadas por espacio")
    p.add_argument("--schema", default="titulo:str,precio:float,promo:str")
    p.add_argument("--min", default="5")
    args = p.parse_args()

    schema = parse_schema(args.schema)
    todo = []
    resumen = []

    for url in args.urls:
        tienda = urlparse(url).netloc.replace("www.", "")
        print(f"\n=== {tienda} ===")
        try:
            data = run_scraper(url, schema, min_items=int(args.min))
            for item in data:
                item["tienda"] = tienda      # etiqueta de origen
            todo.extend(data)
            resumen.append((tienda, len(data), "OK"))
        except Exception as e:
            # Un supermercado bloqueado NO debe hundir la comparacion entera
            print(f"Fallo en {tienda}: {e}")
            resumen.append((tienda, 0, "FALLO"))

    print("\n=== RESUMEN ===")
    for tienda, n, estado in resumen:
        print(f"{tienda}: {n} items ({estado})")

    os.makedirs("outputs", exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"outputs/comparacion_{stamp}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(todo, f, ensure_ascii=False, indent=2)
    print(f"\nGuardado en: {path}")


if __name__ == "__main__":
    main()