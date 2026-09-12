"""Pruebas de las reglas de negocio del agregado Ejemplo (dominio aislado)."""
import pytest

from seedwork.dominio.excepciones import ReglaNegocioExcepcion
from modulos.ejemplo.dominio.fabricas import FabricaEjemplo
from modulos.ejemplo.dominio.objetos_valor import Nombre, EstadoEjemplo
from modulos.ejemplo.dominio.eventos import EjemploCreado


def test_crear_ejemplo_valido_emite_evento():
    ejemplo = FabricaEjemplo().crear_ejemplo(Nombre("prueba"))
    assert ejemplo.estado == EstadoEjemplo.CREADO
    assert len(ejemplo.eventos) == 1
    assert isinstance(ejemplo.eventos[0], EjemploCreado)
    assert ejemplo.eventos[0].nombre == "prueba"


def test_nombre_vacio_viola_regla():
    with pytest.raises(ReglaNegocioExcepcion):
        FabricaEjemplo().crear_ejemplo(Nombre("   "))
