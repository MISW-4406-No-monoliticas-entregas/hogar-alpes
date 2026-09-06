"""Esquemas base de mensajes Avro (v1)."""
from pulsar.schema import Record, String, Long, Integer


class Mensaje(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()


class EventoIntegracion(Mensaje):
    ...


class ComandoIntegracion(Mensaje):
    ...
