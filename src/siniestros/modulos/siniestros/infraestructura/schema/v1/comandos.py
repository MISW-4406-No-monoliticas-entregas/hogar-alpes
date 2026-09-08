"""Esquema Avro v1 del comando RegistrarSiniestro por el broker."""
from pulsar.schema import Record, String, Float

from seedwork.infraestructura.schema.v1.mensajes import ComandoIntegracion


class RegistrarSiniestroPayload(Record):
    partner_id = String()
    poliza = String()
    monto = Float()
    moneda = String()
    calle = String()
    ciudad = String()
    pais = String()


class ComandoRegistrarSiniestro(ComandoIntegracion):
    data = RegistrarSiniestroPayload()
