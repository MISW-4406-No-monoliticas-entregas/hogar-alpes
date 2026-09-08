"""Adaptadores base para Apache Pulsar."""
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
    def __init__(self, url_broker: str):
        self._url_broker = url_broker

    @abstractmethod
    def suscribirse(self):
        ...
