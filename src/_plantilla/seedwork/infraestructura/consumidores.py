"""Consumidor base del broker.

Trío que responde al escenario 7 (caída de una réplica):
  1. Suscripción Key_Shared con `partition_key` = id de la entidad: al perder una
     réplica, Pulsar reasigna sus llaves a otra réplica preservando el orden por
     entidad (Shared no lo garantiza).
  2. `acknowledge` DESPUÉS de que el handler confirmó su Unidad de Trabajo: si el
     proceso muere antes del ack, el mensaje se reentrega.
  3. `negative_acknowledge` en error: reentrega inmediata en vez de esperar el
     timeout de reconocimiento.
La idempotencia (no aplicar dos veces un mensaje reentregado) la garantiza cada
handler registrando el id del mensaje en su misma transacción (ver idempotencia.py).

Además despacha por el campo `type` del sobre a varios handlers, para que un mismo
tópico transporte varios tipos de comando/evento con un solo esquema (BACKWARD).
"""
import logging
import time
from typing import Callable

import pulsar
from pulsar.schema import AvroSchema

from seedwork.infraestructura.pulsar import obtener_cliente

logger = logging.getLogger(__name__)


class ConsumidorBase:
    def __init__(
        self,
        url_broker: str,
        topico: str,
        suscripcion: str,
        schema_sobre,
        manejadores: dict[str, Callable],
    ):
        # manejadores: { "TipoDeMensaje": handler(sobre) -> None }
        self._url_broker = url_broker
        self._topico = topico
        self._suscripcion = suscripcion
        self._schema_sobre = schema_sobre
        self._manejadores = manejadores

    def iniciar(self):
        cliente = obtener_cliente(self._url_broker)
        consumidor = cliente.subscribe(
            self._topico,
            subscription_name=self._suscripcion,
            consumer_type=pulsar.ConsumerType.KeyShared,
            schema=AvroSchema(self._schema_sobre),
        )
        logger.info("Consumidor de %s iniciado (Key_Shared)", self._topico)
        while True:
            mensaje = consumidor.receive()
            try:
                sobre = mensaje.value()
                handler = self._manejadores.get(sobre.type)
                if handler is None:
                    # Tipo que este servicio no maneja: se descarta con ack para
                    # no reentregarlo en bucle.
                    logger.debug("Tipo no manejado '%s'; se ignora", sobre.type)
                    consumidor.acknowledge(mensaje)
                    continue
                handler(sobre)                    # abre UoW, idempotencia + negocio, commit
                consumidor.acknowledge(mensaje)   # ack DESPUÉS del commit
            except Exception:
                logger.exception("Error procesando mensaje; se reintentará (nack)")
                consumidor.negative_acknowledge(mensaje)
                time.sleep(1)
