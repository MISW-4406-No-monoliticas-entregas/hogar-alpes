"""Esquema Avro v1 del comando RegistrarSiniestro.

COPIADO TAL CUAL de src/siniestros/.../schema/v1/comandos.py. El dueño del esquema
de un comando es quien lo consume (Siniestros): S9 solo lo produce, así que debe
publicar EXACTAMENTE el esquema que Siniestros registró en comandos.siniestros.
No modificar aquí sin coordinar con el dueño del comando.
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
