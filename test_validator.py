from validator import DataValidator

schema = {"titulo": "str", "precio": "float"}
v = DataValidator(schema)

# Caso 1: datos validos
ok = [{"titulo": "Libro A", "precio": 10.5}, {"titulo": "Libro B", "precio": 20.0}]
print("Caso 1 (valido):", v.validate(ok))

# Caso 2: tipo incorrecto
bad_type = [{"titulo": "Libro A", "precio": "no-es-numero"}]
print("Caso 2 (tipo):", v.validate(bad_type))

# Caso 3: campo faltante
missing = [{"titulo": "Libro A"}]
print("Caso 3 (faltante):", v.validate(missing))

# Caso 4: campo nulo
null = [{"titulo": None, "precio": 10.5}]
print("Caso 4 (nulo):", v.validate(null))

# Caso 5: lista vacia (simula selector CSS roto)
print("Caso 5 (vacia):", v.validate([]))
