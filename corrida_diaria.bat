@echo off
cd /d "E:\Nueva carpeta\agente-scraper-loop"
.venv\Scripts\python.exe scraper.py --url https://books.toscrape.com/ --schema "titulo:str,precio:float" --min 5
