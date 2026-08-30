"""
validator.py - Validador de datos usando Pydantic (Fase 4 del Loop).
Convierte un esquema dinamico en un modelo Pydantic estricto y valida
que la extraccion sea perfectamente consistente.
"""

from pydantic import ValidationError, create_model


# Mapeo de nombres de tipo (del esquema) a tipos de Python
TYPE_MAP = {
    "str": str,
    "string": str,
    "int": int,
    "integer": int,
    "float": float,
    "number": float,
    "bool": bool,
    "boolean": bool,
}


class DataValidator:
    def __init__(self, schema: dict):
        """
        Construye dinamicamente un modelo Pydantic a partir del esquema.

        Args:
            schema: {"titulo": "str", "precio": "float"}
        """
        fields = {}
        for name, type_name in schema.items():
            py_type = TYPE_MAP.get(type_name, str)
            fields[name] = (py_type, ...)  # ... = campo obligatorio
        self.model = create_model("DynamicSchema", **fields)
        self.schema = schema

    def validate(self, data) -> tuple:
        """
        Valida los datos extraidos contra el esquema.

        Args:
            data: lista de dicts (registros) o un solo dict

        Returns:
            (is_valid, error_message) - El error se alimenta al LLM
            para la auto-correccion del Loop.
        """
        if data is None:
            return False, "El executor no devolvio datos (data es None)"

        records = data if isinstance(data, list) else [data]

        if len(records) == 0:
            return False, "La extraccion devolvio una lista vacia (0 registros). Posible selector CSS roto."

        errors = []
        for i, record in enumerate(records):
            if not isinstance(record, dict):
                errors.append(f"Registro {i}: no es un objeto JSON, recibio {type(record).__name__}")
                continue
            try:
                self.model(**record)
            except ValidationError as e:
                for err in e.errors():
                    campo = ".".join(str(loc) for loc in err["loc"])
                    errors.append(f"Registro {i}: campo '{campo}' -> {err['msg']}")

        if errors:
            return False, "; ".join(errors[:5])
        return True, ""
