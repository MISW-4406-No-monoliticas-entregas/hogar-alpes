"""Esquema Avro v1 del comando que llega por el broker (tópico comandos.siniestros).

Permite que RegistrarSiniestro entre tanto por HTTP (API) como por Pulsar. El
consumidor lo traduce al comando de aplicación y lo despacha por el mediador.
"""
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
