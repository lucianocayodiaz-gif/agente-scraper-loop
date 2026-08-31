"""Tests offline del validador Pydantic dinamico."""
from validator import DataValidator


def v():
    return DataValidator({"titulo": "str", "precio": "float"})


def test_datos_validos():
    ok, err = v().validate([{"titulo": "A", "precio": 1.5}])
    assert ok is True and err == ""


def test_tipo_incorrecto():
    ok, err = v().validate([{"titulo": "A", "precio": "no-numero"}])
    assert ok is False and "precio" in err


def test_campo_faltante():
    ok, err = v().validate([{"titulo": "A"}])
    assert ok is False


def test_campo_nulo():
    ok, err = v().validate([{"titulo": None, "precio": 1.0}])
    assert ok is False


def test_lista_vacia():
    ok, err = v().validate([])
    assert ok is False and "vacia" in err
