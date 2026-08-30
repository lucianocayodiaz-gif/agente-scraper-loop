"""
llm_client.py - Cliente de IA para comunicarse con el LLM.
Usa el SDK de OpenAI apuntando a Groq (compatible).
"""

from openai import OpenAI
from config import GROQ_API_KEY, LLM_MODEL


class LLMClient:
    def __init__(self):
        """Inicializa el cliente de Groq usando el SDK de OpenAI."""
        self.client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = LLM_MODEL

    def chat(self, prompt: str) -> str:
        """Envía un prompt simple y devuelve la respuesta de texto."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content

    def generate_code(self, prompt: str) -> str:
        """
        Fase 2 del Loop: genera código Python a partir de un prompt.

        Args:
            prompt: Instrucción para el LLM (DOM, esquema, etc.)

        Returns:
            Código Python limpio (sin markdown).
        """
        system_prompt = (
            "Eres un experto en web scraping con Python. "
            "Genera UNICAMENTE codigo Python, sin explicaciones. "
            "El codigo debe imprimir el resultado como JSON en stdout."
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return self._extract_code(response.choices[0].message.content)

    def generate_code_with_history(self, prompt: str, previous_code: str, error: str) -> str:
        """
        Fase 4 -> 2 del Loop: genera código corregido usando el error.

        Args:
            prompt: Instrucción original
            previous_code: Código que falló
            error: Mensaje de error capturado

        Returns:
            Código Python corregido.
        """
        correction_prompt = (
            f"{prompt}\n\n"
            f"El siguiente codigo fallo:\n{previous_code}\n\n"
            f"Error obtenido:\n{error}\n\n"
            "Corrige el codigo y devuelve UNICAMENTE el codigo corregido."
        )
        return self.generate_code(correction_prompt)

    @staticmethod
    def _extract_code(text: str) -> str:
        """Extrae el código limpio eliminando bloques markdown."""
        if "```python" in text:
            return text.split("```python")[1].split("```")[0].strip()
        if "```" in text:
            return text.split("```")[1].split("```")[0].strip()
        return text.strip()
