"""Fase C: tabla de comparacion de precios entre tiendas.
Uso: python tabla.py [ruta_json]  (sin ruta: toma la ultima comparacion)"""
import glob
import json
import re
import sys
from collections import defaultdict


def normalizar(titulo):
    """'Coca-Cola 2 Lts' == 'coca cola 2000ml' == 'Coca Cola 2L'."""
    t = titulo.lower()
    t = t.replace("lts", "l").replace("lt", "l")
    t = re.sub(r"(\d+)\s*ml\b",
               lambda m: str(int(m.group(1)) // 1000) + "l" if int(m.group(1)) >= 1000 else m.group(0), t)
    t = re.sub(r"(\d+)\s+(l|ml|kg|g|un)\b", r"\1\2", t)
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("outputs/comparacion_*.json"))[-1]
    data = json.load(open(path, encoding="utf-8"))

    por_producto = defaultdict(dict)
    for item in data:
        por_producto[normalizar(item.get("titulo", ""))][item.get("tienda", "?")] = item

    print(f"\n=== COMPARACION ({path}) ===")
    encontrados = 0
    for clave, tiendas in sorted(por_producto.items()):
        precios = {t: it for t, it in tiendas.items() if isinstance(it.get("precio"), (int, float))}
        if len(precios) < 2:
            continue
        encontrados += 1
        mas_barato = min(precios, key=lambda t: precios[t]["precio"])
        partes = []
        for t, it in sorted(precios.items(), key=lambda kv: kv[1]["precio"]):
            promo = f" [{it['promo']}]" if it.get("promo") else ""
            estrella = " ⭐" if t == mas_barato else ""
            partes.append(f"{t}: ${it['precio']}{promo}{estrella}")
        print(f"· {clave}\n    " + " | ".join(partes))
    if not encontrados:
        print("(ningun producto aparece en mas de una tienda en este archivo)")


if __name__ == "__main__":
    main()