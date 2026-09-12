"""Adaptadores base para Apache Pulsar.

Mejora vs. E3: se reutiliza UN solo `pulsar.Client` por proceso y UN productor
por (tópico, esquema). En la E3 el despachador abría y cerraba un cliente por
mensaje; bajo el pico 4x de ingesta eso era el cuello de botella (handshake TCP
+ lookup + registro de esquema en cada envío). Aquí el cliente y los productores
viven mientras viva el proceso.
"""
import threading
from abc import ABC, abstractmethod

import pulsar
from pulsar.schema import AvroSchema

# Cliente único y caché de productores, protegidos con doble verificación
# porque el consumidor corre en un hilo aparte del de Flask.
_cliente = None
_cliente_lock = threading.Lock()
_productores: dict = {}
_productores_lock = threading.Lock()


def obtener_cliente(url_broker: str) -> "pulsar.Client":
    global _cliente
    if _cliente is None:
        with _cliente_lock:
            if _cliente is None:
                _cliente = pulsar.Client(url_broker)
    return _cliente


def _obtener_productor(url_broker: str, topico: str, schema_record):
    clave = (topico, schema_record.__name__)
    productor = _productores.get(clave)
    if productor is None:
        with _productores_lock:
            productor = _productores.get(clave)
            if productor is None:
                productor = obtener_cliente(url_broker).create_producer(
                    topico, schema=AvroSchema(schema_record)
                )
                _productores[clave] = productor
    return productor


def cerrar_cliente() -> None:
    """Cierra el cliente y los productores (al apagar el proceso)."""
    global _cliente
    if _cliente is not None:
        _cliente.close()
        _cliente = None
        _productores.clear()


class Despachador(ABC):
    """Adaptador de salida hacia el broker."""

    def __init__(self, url_broker: str):
        self._url_broker = url_broker

    def _publicar_mensaje(
        self, mensaje, topico: str, schema_record, clave_particion: str | None = None
    ):
        # clave_particion => enrutado por Key_Shared: todos los mensajes de la
        # misma entidad caen en la misma partición y el mismo consumidor,
        # preservando el orden por entidad.
        productor = _obtener_productor(self._url_broker, topico, schema_record)
        if clave_particion is not None:
            productor.send(mensaje, partition_key=clave_particion)
        else:
            productor.send(mensaje)

    @abstractmethod
    def publicar_evento(self, evento, topico: str):
        ...
