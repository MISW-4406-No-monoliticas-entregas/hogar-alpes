"""Esquemas Avro v1 de los eventos de integración (tópico eventos.trabajos).

Patrón envoltura + payload (data): la envoltura (id/time/spec_version/type) es
común; el payload es específico del evento. Para evolucionar de forma
retrocompatible (escenario de modificabilidad de la Entrega 4) se crea un
schema/v2 agregando campos OPCIONALES al payload, sin romper a los consumidores.
"""
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
