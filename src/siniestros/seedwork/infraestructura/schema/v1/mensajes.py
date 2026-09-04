"""Esquemas base de mensajes Avro (versión 1).

Todo mensaje de integración lleva una envoltura común (id, time, spec_version,
type) más un payload específico. Versionar en schema/v1 es lo que habilita el
escenario de modificabilidad de la Entrega 4: "evolución retrocompatible de un
esquema de evento" (agregar campos opcionales en un v2 sin romper consumidores).
"""
from pulsar.schema import Record, String, Long, Integer


class Mensaje(Record):
    id = String()
    time = Long()
    spec_version = String()
    type = String()


class EventoIntegracion(Mensaje):
    """Base de los eventos de integración publicados en el broker."""
    ...


class ComandoIntegracion(Mensaje):
    """Base de los comandos que llegan por el broker."""
    ...
