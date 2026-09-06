"""Esquemas Avro v1 de los eventos de integración."""
from pulsar.schema import Record, String, Float

from seedwork.infraestructura.schema.v1.mensajes import EventoIntegracion


class SiniestroRegistradoPayload(Record):
    id_siniestro = String()
    partner_id = String()
    poliza = String()
    monto = Float()
    moneda = String()
    estado = String()


class EventoSiniestroRegistrado(EventoIntegracion):
    data = SiniestroRegistradoPayload()


class ProveedorAsignadoPayload(Record):
    id_siniestro = String()
    proveedor_id = String()
    estado = String()


class EventoProveedorAsignado(EventoIntegracion):
    data = ProveedorAsignadoPayload()
