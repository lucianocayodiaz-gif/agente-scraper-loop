"""
executor.py - Sandbox de ejecución para el código generado por el LLM.
Escribe el código como script temporal (como pide la spec) y lo ejecuta
en un subprocess aislado, capturando stdout, stderr y resultados.
"""

import subprocess
import sys
import json
import os
import tempfile


class CodeExecutor:
    def __init__(self, timeout: int = 30):
        """Inicializa el executor con un timeout de seguridad."""
        self.timeout = timeout

    def execute_code(self, code: str) -> dict:
        """
        Fase 3 del Loop: escribe el código generado como script temporal
        y lo ejecuta en un proceso aislado.
        """
        tmp_path = None
        try:
            # Script temporal: evita el límite de cmdline de Windows
            with tempfile.NamedTemporaryFile(
                "w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(code)
                tmp_path = f.name

            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "output": result.stdout,
                    "data": None,
                    "error": result.stderr,
                }

            return {
                "success": True,
                "output": result.stdout,
                "data": self._parse_json(result.stdout),
                "error": "",
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "data": None,
                "error": f"Timeout: el codigo tardo mas de {self.timeout}s (posible bucle infinito)",
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "data": None,
                "error": str(e),
            }
        finally:
            # Limpieza del script temporal
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    @staticmethod
    def _parse_json(stdout: str):
        """Extrae JSON del stdout, tolerando lineas de ruido (logs de scroll)."""
        text = stdout.strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            pass
        # Modo tolerante: busca el primer [ o { y usa raw_decode
        for start in ("[", "{"):
            idx = text.find(start)
            if idx != -1:
                try:
                    obj, _ = json.JSONDecoder().raw_decode(text[idx:])
                    return obj
                except (json.JSONDecodeError, ValueError):
                    continue
        return None
