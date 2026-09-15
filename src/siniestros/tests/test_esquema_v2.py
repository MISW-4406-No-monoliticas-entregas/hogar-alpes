"""Evolución de esquema v1 -> v2 del sobre de eventos.siniestros (BACKWARD).

v2 agrega `canal_origen` al payload con valor por defecto. Se verifica con
fastavro (el mismo formato Avro que usa Pulsar) que:
  1. Un consumidor v1 lee un mensaje v1 (línea base, nada se rompe).
  2. Un consumidor v2 lee un mensaje v1 y recibe el default del campo nuevo —
     exactamente lo que valida el registry con la política BACKWARD.
  3. Un consumidor v1 lee un mensaje v2 ignorando el campo nuevo (los
     consumidores existentes no se rompen cuando el productor evolucione).
"""
import io

import fastavro

from modulos.siniestros.infraestructura.schema.v1.eventos import EventoSiniestros
from modulos.siniestros.infraestructura.schema.v2.eventos import (
    EventoSiniestros as EventoSiniestrosV2,
)

V1 = fastavro.parse_schema(EventoSiniestros.schema())
V2 = fastavro.parse_schema(EventoSiniestrosV2.schema())

MENSAJE_V1 = {
    "id": "msg-1",
    "time": 1726300000000,
    "spec_version": "v1",
    "type": "SiniestroRegistrado",
    "data": {
        "id_siniestro": "sin-1",
        "partner_id": "partner-1",
        "poliza": "POL-1",
        "monto": 1000.0,
        "moneda": "COP",
        "proveedor_id": "",
        "estado": "REGISTRADO",
        "motivo": "",
    },
}


def _escribir(schema, mensaje) -> bytes:
    buffer = io.BytesIO()
    fastavro.schemaless_writer(buffer, schema, mensaje)
    return buffer.getvalue()


def _leer(datos: bytes, schema_escritor, schema_lector=None):
    return fastavro.schemaless_reader(
        io.BytesIO(datos), schema_escritor, reader_schema=schema_lector
    )


def test_consumidor_v1_lee_mensaje_v1():
    crudo = _escribir(V1, MENSAJE_V1)
    leido = _leer(crudo, V1)
    assert leido["type"] == "SiniestroRegistrado"
    assert leido["data"]["partner_id"] == "partner-1"


def test_consumidor_v2_lee_mensaje_v1_con_default_del_campo_nuevo():
    crudo = _escribir(V1, MENSAJE_V1)
    leido = _leer(crudo, V1, V2)
    assert leido["type"] == "SiniestroRegistrado"
    assert leido["data"]["canal_origen"] == "no_especificado"


def test_consumidor_v1_lee_mensaje_v2_ignorando_el_campo_nuevo():
    mensaje_v2 = dict(MENSAJE_V1)
    mensaje_v2["data"] = dict(MENSAJE_V1["data"], canal_origen="portal_web")
    crudo = _escribir(V2, mensaje_v2)
    leido = _leer(crudo, V2, V1)
    assert leido["data"]["poliza"] == "POL-1"
    assert "canal_origen" not in leido["data"]
