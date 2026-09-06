"""Consumidor del tópico comandos.siniestros."""
import logging
import time

import pulsar
from pulsar.schema import AvroSchema

from config.settings import PULSAR_URL, TOPICO_COMANDOS, SUSCRIPCION
from seedwork.aplicacion.comandos import ejecutar_comando
from modulos.siniestros.aplicacion.comandos.registrar_siniestro import (
    RegistrarSiniestro,
)
from modulos.siniestros.infraestructura.schema.v1.comandos import (
    ComandoRegistrarSiniestro,
)

logger = logging.getLogger(__name__)


def suscribirse_a_comandos(url_broker: str = PULSAR_URL):
    """Consume el tópico comandos.siniestros y despacha cada comando."""
    cliente = pulsar.Client(url_broker)
    consumidor = cliente.subscribe(
        TOPICO_COMANDOS,
        consumer_type=pulsar.ConsumerType.Shared,
        subscription_name=f"{SUSCRIPCION}-comandos",
        schema=AvroSchema(ComandoRegistrarSiniestro),
    )
    logger.info("Consumidor de %s iniciado", TOPICO_COMANDOS)
    try:
        while True:
            mensaje = consumidor.receive()
            try:
                datos = mensaje.value().data
                comando = RegistrarSiniestro(
                    partner_id=datos.partner_id,
                    poliza=datos.poliza,
                    monto=datos.monto,
                    moneda=datos.moneda,
                    calle=datos.calle,
                    ciudad=datos.ciudad,
                    pais=datos.pais,
                )
                ejecutar_comando(comando)
                consumidor.acknowledge(mensaje)
            except Exception:
                logger.exception("Error procesando comando; se reintentará (nack)")
                consumidor.negative_acknowledge(mensaje)
                time.sleep(1)
    finally:
        cliente.close()
