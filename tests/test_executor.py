"""Tests offline del sandbox de ejecucion."""
from executor import CodeExecutor


def test_codigo_exitoso():
    r = CodeExecutor().execute_code('import json\nprint(json.dumps(["a", "b"]))')
    assert r["success"] is True
    assert r["data"] == ["a", "b"]
    assert r["error"] == ""


def test_codigo_con_error():
    r = CodeExecutor().execute_code("print(1/0)")
    assert r["success"] is False
    assert "ZeroDivisionError" in r["error"]


def test_timeout_bucle_infinito():
    r = CodeExecutor(timeout=2).execute_code("while True: pass")
    assert r["success"] is False
    assert "Timeout" in r["error"]


def test_stdout_con_ruido():
    r = CodeExecutor().execute_code('print("scrolling...")\nprint("[1, 2, 3]")')
    assert r["data"] == [1, 2, 3]
