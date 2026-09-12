"""Pruebas de las reglas del agregado Sincronizacion (dominio aislado)."""
import pytest

from seedwork.dominio.excepciones import ReglaNegocioExcepcion
from modulos.sincronizaciones.dominio.fabricas import FabricaSincronizacion
from modulos.sincronizaciones.dominio.objetos_valor import (
    EstadoSincronizacion,
    IdExterno,
)
from modulos.sincronizaciones.dominio.eventos import SiniestroSincronizado

CANONICO = {
    "partner_id": "seguros-alpes",
    "id_externo": "SA-1",
    "poliza": "POL-9",
    "monto": 500000.0,
    "moneda": "COP",
    "calle": "Cra 7 # 1-2",
    "ciudad": "Bogota",
    "pais": "CO",
}


def test_sincronizar_valido_emite_evento_y_pasa_a_publicada():
    s = FabricaSincronizacion().crear_sincronizacion("seguros-alpes", "SA-1")
    assert s.estado == EstadoSincronizacion.RECIBIDA
    s.sincronizar(CANONICO)
    assert s.estado == EstadoSincronizacion.PUBLICADA
    assert len(s.eventos) == 1
    evento = s.eventos[0]
    assert isinstance(evento, SiniestroSincronizado)
    assert evento.partner_id == "seguros-alpes"
    assert evento.id_externo == "SA-1"
    assert evento.poliza == "POL-9"


def test_id_externo_vacio_viola_regla():
    s = FabricaSincronizacion().crear_sincronizacion("seguros-alpes", "  ")
    with pytest.raises(ReglaNegocioExcepcion):
        s.sincronizar(CANONICO)
