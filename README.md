# 🤖 Agente Scraper Autónomo — Loop Engineering

Sistema de web scraping que se **auto-corrige** cuando falla. Usa **Loop Engineering** e IA generativa (vía Groq, 100% gratis) para reescribir su propio código de extracción cuando un sitio web cambia su estructura.

## 🎯 El problema que resuelve

Los scrapers tradicionales se rompen silenciosamente cuando un sitio cambia una clase CSS o su DOM. Mantenerlos consume hasta el 80% del tiempo de un equipo de datos.

**Este agente lo resuelve:** si el scraper falla, la IA lee el error, re-analiza el DOM y **reescribe su propio código** hasta que Pydantic valida los datos. Sin intervención humana.

## 🔄 Cómo funciona (Loop de 4 fases)

```
[1. Planificación / Análisis DOM]
              │
              ▼
[2. Generación de código (LLM)]
              │
              ▼
[3. Ejecución en sandbox] ◄────────┐
              │                    │ (si falla)
              ▼                    │
[4. Validación Pydantic] ──────────┘
              │ (si es exitoso)
              ▼
      [ JSON / CSV versionado ]
```

1. **Planificación:** recibe URL + esquema, obtiene el HTML y construye un mapa DOM simplificado.
2. **Generación:** el LLM escribe código Python (BeautifulSoup) que imprime JSON en stdout.
3. **Ejecución:** el código corre en un subprocess aislado con timeout; se capturan stdout/stderr.
4. **Validación:** Pydantic dinámico valida tipos, campos obligatorios y listas no vacías. Si falla, el error + código fallido se retroalimentan al LLM.

## 🛠️ Stack tecnológico

- **Python 3.11+**
- **BeautifulSoup4** — parsing del DOM
- **Pydantic v2** — validación estricta con esquemas dinámicos (`create_model`)
- **Groq API** — inferencia gratuita y ultrarrápida (`openai/gpt-oss-20b`)
- **OpenAI SDK** — cliente estándar compatible con Groq
- **Playwright** — sitios dinámicos (implementado: scrolls y paginación autónoma)

## 🚀 Instalación

```bash
git clone https://github.com/lucianocayodiaz-gif/agente-scraper-loop.git
cd agente-scraper-loop

python -m venv .venv
.venv\Scripts\activate          # Windows

pip install -r requirements.txt
python -m playwright install chromium
```

Crea tu `.env` con una key gratuita de [console.groq.com](https://console.groq.com/keys):

```
GROQ_API_KEY=gsk_xxxx
LLM_MODEL=openai/gpt-oss-20b
MAX_ITERATIONS=3
```

## 📖 Uso

```python
from main import run_scraper

schema = {"titulo": "str", "precio": "float"}
data = run_scraper("test_sites/site_v1.html", schema)
```

## 🎬 Demo de auto-corrección

`demo_autocorreccion.py` simula el Escenario 1 de la spec: el sitio cambia sus clases CSS (v1 → v2) y un scraper heredado se rompe.

```bash
python demo_autocorreccion.py
```

Salida real:

```
🔄 Iteracion 1/3
❌ Fallo detectado: La extraccion devolvio una lista vacia (0 registros). Posible selector CSS roto.
🔧 Auto-correccion: pidiendo fix al LLM...

🔄 Iteracion 2/3
✅ Datos validos en iteracion 2
💾 Guardado en: outputs\scrape_20260830_195349.json

🏆 DEMO COMPLETA: el agente se auto-corrigio sin intervencion humana
```

## 🧪 Escenarios de calidad

| Escenario | Estado |
|---|---|
| Cambio de clase/selector CSS | ✅ Implementado (demo en vivo) |
| Campos vacíos/nulos | ✅ Pydantic rechaza y retroalimenta al loop |
| Infinite scroll | ✅ Playwright con scrolls progresivos (fallback a HTTP en la nube) |

## 📁 Estructura

```
agente-scraper-loop/
├── main.py            # Orquestador del loop (4 fases + memoria + metricas + etica)
├── llm_client.py      # Cliente IA (Groq) + limpieza de markdown
├── executor.py        # Sandbox subprocess con timeout
├── validator.py       # Validacion Pydantica dinamica
├── config.py          # Config central (.env / secrets)
├── scraper.py         # CLI para usuarios
├── app.py             # UI Streamlit para no tecnicos
├── tests/             # Suite pytest offline (CI)
├── test_sites/        # HTMLs v1/v2 que simulan cambios de DOM
└── outputs/           # JSONs versionados + metricas + memoria
```

## 🔒 Seguridad y decisiones de ingeniería

- Credenciales en `.env` fuera del control de versiones; incidente real de push protection (secret scanning) resuelto con purga de historial y rotación de clave.
- Código del LLM ejecutado en **subprocess con timeout** (no `exec()`), protegiendo la memoria del agente y la máquina.
- HTML inyectado al código generado vía **base64** (sin escapado, sin acceso a red desde el código generado).
- `MAX_ITERATIONS` y simplificación del DOM para **control de costos de tokens**.

---

## 🧠 Capas de producto

- **Memoria de selectores:** si el agente ya corrigió un sitio, reutiliza el código exitoso en la próxima corrida (3.8s → 1.5s, 0 tokens).
- **Métricas por corrida:** cada extracción queda en `outputs/metrics.json` (URL, éxito, iteraciones, items, segundos).
- **Navegación autónoma:** paga 50 páginas solo cuando se lo piden (`--min 50`), eligiendo Playwright (local) o HTTP (nube) según el entorno.
- **Ética:** consulta `robots.txt` antes de scrapear; si el sitio dice "no", se abstiene.
- **Alertas:** corridas fallidas registradas en `outputs/alertas.log`.

## 🖥️ UI para no técnicos

`iniciar_app.bat` abre la app Streamlit en el navegador: URL + campos + botón. Historial de corridas y descarga de JSON incluidos.

## 🌐 Demo online

🔗 https://agente-scraper-loop-klci3rdd833dklwbomh4os.streamlit.app
(Contraseña de acceso: pedírsela al autor)

## 📊 Incidentes reales resueltos

| Incidente | Causa | Resolución |
|---|---|---|
| Push rechazado por secret scanning | Credencial commiteada por error | Purga de historial + rotación de clave |
| WinError 206 en el executor | Límite de 32KB en cmdline de Windows | Código en archivos temporales |
| ModuleNotFoundError: requests | Sandbox sin librería común | Contrato de sandbox en el prompt |
| Modelo deprecado (llama3-8b) | Default hardcodeado viejo | Default nuevo + modelo en secrets |
| Wheels de pydantic-core en cloud | Pin estricto sin wheel | Split runtime/dev de dependencias |
| HF cambió tier gratis a pago | Cambio externo de plataforma | Pivot a Streamlit Community Cloud |

Proyecto de portafolio que demuestra: Python, IA generativa, web scraping, arquitectura de software y buenas prácticas de Git/seguridad.
