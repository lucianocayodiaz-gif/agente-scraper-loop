"""
app.py - Interfaz visual del Agente Scraper Autonomo (Streamlit).
Cualquier persona puede usarlo: escribe la URL, define los datos y presiona el boton.
Ejecutar: streamlit run app.py  (o doble clic en iniciar_app.bat)
"""

import json

import streamlit as st

from main import run_scraper, cargar_memoria, METRICS_PATH, _leer_json

st.set_page_config(page_title="Agente Scraper Autonomo", page_icon="🤖", layout="wide")

st.title("🤖 Agente Scraper Autonomo")
st.caption("Loop Engineering: el agente genera, ejecuta y auto-corrige su propio codigo de extraccion.")

with st.sidebar:
    st.header("⚙️ Configuracion")
    url = st.text_input("URL o archivo HTML", value="https://books.toscrape.com/")
    schema_text = st.text_area(
        "Datos a extraer (campo:tipo por linea)",
        value="titulo:str\nprecio:float",
        help="Tipos validos: str, float, int, bool",
    )
    min_items = st.number_input("Minimo de registros esperados", min_value=1, value=5)
    st.divider()
    st.subheader("🧠 Memoria")
    if url in cargar_memoria():
        st.success("Este sitio ya tiene codigo aprendido ✅")
    else:
        st.info("Sitio nuevo: el agente generara codigo desde cero.")


def parse_schema(texto: str) -> dict:
    schema = {}
    for linea in texto.strip().splitlines():
        if ":" in linea:
            nombre, tipo = linea.split(":", 1)
            schema[nombre.strip()] = tipo.strip()
    return schema


if st.button("🚀 EJECUTAR AGENTE", type="primary"):
    schema = parse_schema(schema_text)
    if not schema:
        st.error("Define al menos un campo, ejemplo: titulo:str")
    else:
        with st.status("🤖 El agente esta trabajando…", expanded=True) as status:
            def progress(msg):
                st.write(msg)

            data = run_scraper(url, schema, min_items=int(min_items), progress=progress)

            if data:
                status.update(label="✅ Agente completado", state="complete")
            else:
                status.update(label="⛔ Agente sin datos", state="error")

        if data:
            st.subheader(f"📦 Resultados ({len(data)} registros)")
            st.dataframe(data)
            json_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            st.download_button(
                "⬇️ Descargar JSON",
                data=json_bytes,
                file_name="extraccion.json",
                mime="application/json",
            )
        else:
            st.error("El agente no pudo extraer datos esta vez. Revisa el detalle de fases arriba.")

st.divider()
st.subheader("📈 Historial de corridas")
historial = _leer_json(METRICS_PATH, [])
if historial:
    st.dataframe(list(reversed(historial))[:20])
else:
    st.info("Todavia no hay corridas registradas.")
