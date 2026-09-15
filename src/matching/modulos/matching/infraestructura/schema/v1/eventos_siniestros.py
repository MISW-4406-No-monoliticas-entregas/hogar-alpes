"""Copia (lado consumidor) del esquema Avro v1 de eventos.siniestros (S2).

Cada servicio es dueño del esquema de lo que publica; el consumidor copia ese
esquema en su propio schema/v1/ en vez de importar código de S2. S7 solo
loguea estos eventos (sin lógica de negocio todavía), por eso `data` cubre
ambos tipos que hoy viajan por el tópico: SiniestroRegistrado y el
ProveedorAsignado interno de S2 (no confundir con el ProveedorAsignado propio
de S7 en eventos.matching).
"""
from pulsar.schema import Record, String, Long, Float


class DatosEventoSiniestros(Record):
    id_siniestro = String(required=False, default="")
    partner_id = String(required=False, default="")
    poliza = String(required=False, default="")
    monto = Float(required=False, default=0.0)
    moneda = String(required=False, default="")
    proveedor_id = String(required=False, default="")
    estado = String(required=False, default="")


class EventoSiniestros(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()  # "SiniestroRegistrado" | "ProveedorAsignado" (de S2)
    data = DatosEventoSiniestros()
