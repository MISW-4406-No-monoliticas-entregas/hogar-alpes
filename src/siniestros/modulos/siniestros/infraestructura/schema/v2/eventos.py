"""Esquema Avro v2 del tópico eventos.siniestros — NO ACTIVO.

Evolución BACKWARD-compatible del sobre v1: agrega UN campo nuevo con valor por
defecto (`canal_origen`) al payload. Un consumidor que solo conoce v1 sigue
leyendo mensajes v1 sin romperse, y un consumidor v2 que lea un mensaje v1
obtiene el default (ver tests/test_esquema_v2.py).

Las clases se llaman IGUAL que en v1 (por eso viven en su propio módulo): el
nombre del record es parte del esquema Avro y la resolución/compatibilidad
exige que coincida entre versiones. Importar con alias:

    from ...schema.v2.eventos import EventoSiniestros as EventoSiniestrosV2

Este esquema existe para demostrar la evolución en el registry; el despachador
sigue publicando con v1 a propósito. Activarlo = cambiar el import del
despachador y poblar `canal_origen`.
"""
from pulsar.schema import Record, String, Float, Long


class DatosSiniestro(Record):
    id_siniestro = String(required=False, default="")
    partner_id = String(required=False, default="")
    poliza = String(required=False, default="")
    monto = Float(required=False, default=0.0)
    moneda = String(required=False, default="")
    proveedor_id = String(required=False, default="")
    estado = String(required=False, default="")
    motivo = String(required=False, default="")
    # Campo NUEVO en v2, con default => compatible hacia atrás. required_default
    # hace que el default viaje en el esquema Avro (sin él, pulsar lo omite y el
    # lector v2 no podría resolver un mensaje v1).
    canal_origen = String(required=False, default="no_especificado", required_default=True)


class EventoSiniestros(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()
    data = DatosSiniestro()
