"""Esquema Avro v1 del evento de integración SiniestroSincronizado (eventos.partners).

S9 es dueño de este tópico. Sobre único con `type`, y los campos del sobre van
declarados en la clase concreta (pulsar.schema no hereda de la base).
"""
from pulsar.schema import Record, String, Long


class DatosSiniestroSincronizado(Record):
    id_sincronizacion = String(required=False, default="")
    partner_id = String(required=False, default="")
    id_externo = String(required=False, default="")
    estado = String(required=False, default="")


class EventoSiniestroSincronizado(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()  # "SiniestroSincronizado"
    data = DatosSiniestroSincronizado()
