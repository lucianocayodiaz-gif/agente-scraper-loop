from executor import CodeExecutor

ex = CodeExecutor(timeout=5)

# Caso 1: codigo que funciona e imprime JSON
good = 'import json\nprint(json.dumps(["Libro A", "Libro B"]))'
r1 = ex.execute_code(good)
print("Caso 1 (exito):", r1)

# Caso 2: codigo con error de ejecucion
bad = 'print(1/0)'
r2 = ex.execute_code(bad)
print("Caso 2 (error):", r2["success"], "|", r2["error"].strip().splitlines()[-1])

# Caso 3: bucle infinito -> debe morir por timeout
loop = 'while True: pass'
r3 = ex.execute_code(loop)
print("Caso 3 (timeout):", r3["success"], "|", r3["error"])
