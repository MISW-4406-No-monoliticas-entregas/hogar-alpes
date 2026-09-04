"""Adaptadores base para Apache Pulsar (puertos de salida/entrada al broker).

- Despachador: publica eventos/comandos de integración con esquema Avro.
- Consumidor: escucha un tópico y delega el mensaje a un handler.

Son clases base; cada módulo define su Despachador/Consumidor concretos con sus
esquemas Avro (schema/v1). El dominio no conoce ninguna de estas clases.
"""
from abc import ABC, abstractmethod

import pulsar
from pulsar.schema import AvroSchema


class Despachador(ABC):
    def __init__(self, url_broker: str):
        self._url_broker = url_broker

    def _publicar_mensaje(self, mensaje, topico: str, schema_record):
        cliente = pulsar.Client(self._url_broker)
        try:
            productor = cliente.create_producer(
                topico, schema=AvroSchema(schema_record)
            )
            productor.send(mensaje)
        finally:
            cliente.close()

    @abstractmethod
    def publicar_evento(self, evento, topico: str):
        ...


class Consumidor(ABC):
    """Adaptador de entrada: consume un tópico de Pulsar en un hilo propio."""

    def __init__(self, url_broker: str):
        self._url_broker = url_broker

    @abstractmethod
    def suscribirse(self):
        ...
