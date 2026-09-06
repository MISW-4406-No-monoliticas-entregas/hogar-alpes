"""Pruebas del flujo de eventos de dominio hacia la proyección."""
import pytest

from seedwork.aplicacion.eventos import despachar_evento_dominio
from modulos.siniestros.dominio.eventos import (
    SiniestroRegistrado,
    ProveedorAsignado,
)
from modulos.seguimiento.aplicacion import handlers as seguimiento_handlers


class RepositorioFake:
    """Doble de prueba de la proyección: captura los upserts en memoria."""

    def __init__(self):
        self.filas = {}

    def registrar_o_actualizar(self, **campos):
        self.filas.setdefault(campos["id_siniestro"], {}).update(campos)


@pytest.fixture
def proyeccion(monkeypatch):
    fake = RepositorioFake()
    monkeypatch.setattr(seguimiento_handlers, "_repositorio", fake)
    seguimiento_handlers.registrar_handlers()
    return fake


def test_siniestro_registrado_actualiza_la_proyeccion(proyeccion):
    despachar_evento_dominio(
        SiniestroRegistrado(
            id_siniestro="s-1",
            partner_id="partner-1",
            poliza="POL-1",
            monto=1000.0,
            moneda="COP",
            estado="REGISTRADO",
        )
    )
    fila = proyeccion.filas["s-1"]
    assert fila["partner_id"] == "partner-1"
    assert fila["estado"] == "REGISTRADO"
    assert fila["monto"] == 1000.0


def test_proveedor_asignado_actualiza_la_proyeccion(proyeccion):
    despachar_evento_dominio(
        SiniestroRegistrado(
            id_siniestro="s-2", partner_id="partner-2", poliza="POL-2",
            monto=50.0, moneda="COP", estado="REGISTRADO",
        )
    )
    despachar_evento_dominio(
        ProveedorAsignado(id_siniestro="s-2", proveedor_id="prov-7", estado="ASIGNADO")
    )
    fila = proyeccion.filas["s-2"]
    assert fila["estado"] == "ASIGNADO"
    assert fila["proveedor_id"] == "prov-7"
    assert fila["partner_id"] == "partner-2"
