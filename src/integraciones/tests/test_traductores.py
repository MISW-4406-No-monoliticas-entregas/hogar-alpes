"""Pruebas de los traductores por partner (ACL de entrada)."""
import pytest

from modulos.sincronizaciones.aplicacion.traductores.registro import (
    registro_de_traductores,
    PartnerDesconocido,
)
from modulos.sincronizaciones.aplicacion.traductores.base import ErrorTraduccion


def test_traductor_seguros_alpes():
    payload = {
        "numeroReclamo": "SA-2026-001",
        "poliza": "POL-9",
        "montoEstimado": 500000,
        "moneda": "COP",
        "direccion": {"calle": "Cra 7 # 1-2", "ciudad": "Bogota", "pais": "CO"},
    }
    t = registro_de_traductores.resolver("seguros-alpes")
    c = t.traducir("seguros-alpes", payload)
    assert c.id_externo == "SA-2026-001"
    assert c.poliza == "POL-9"
    assert c.monto == 500000.0
    assert c.calle == "Cra 7 # 1-2"
    assert c.ciudad == "Bogota"


def test_traductor_banco_andes_formato_distinto():
    payload = {
        "ref": "BA-778",
        "policy_number": "POL-12",
        "amount": {"value": 1200000, "currency": "COP"},
        "address": "Calle 1 # 2-3, Bogota, CO",
    }
    t = registro_de_traductores.resolver("banco-andes")
    c = t.traducir("banco-andes", payload)
    assert c.id_externo == "BA-778"
    assert c.poliza == "POL-12"
    assert c.monto == 1200000.0
    assert c.moneda == "COP"
    assert c.calle == "Calle 1 # 2-3"
    assert c.ciudad == "Bogota"
    assert c.pais == "CO"


def test_partner_desconocido():
    with pytest.raises(PartnerDesconocido):
        registro_de_traductores.resolver("partner-inexistente")


def test_payload_invalido_banco_andes():
    t = registro_de_traductores.resolver("banco-andes")
    with pytest.raises(ErrorTraduccion):
        t.traducir("banco-andes", {"ref": "BA-1"})  # faltan campos
