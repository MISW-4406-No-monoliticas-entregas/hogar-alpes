"""Consumidor del tópico comandos.matching.

Usa el ConsumidorBase del seedwork (Key_Shared + ack tardío + nack) y despacha
por `type` del sobre: "AsignarProveedor" y "LiberarProveedor".
"""
from config.settings import PULSAR_URL, TOPICO_COMANDOS, SUSCRIPCION
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.infraestructura.consumidores import ConsumidorBase
from modulos.matching.aplicacion.comandos.asignar_proveedor import AsignarProveedor
from modulos.matching.aplicacion.comandos.liberar_proveedor import LiberarProveedor
from modulos.matching.infraestructura.schema.v1.comandos import ComandoMatching


def _al_asignar_proveedor(sobre):
    # `sobre.id` es el id del mensaje del broker => idempotencia atómica en el handler.
    ejecutar_comando(
        AsignarProveedor(
            id_siniestro=sobre.data.id_siniestro,
            servicio=sobre.data.servicio,
            zona=sobre.data.zona,
            id_mensaje=sobre.id,
        )
    )


def _al_liberar_proveedor(sobre):
    ejecutar_comando(
        LiberarProveedor(
            id_siniestro=sobre.data.id_siniestro,
            proveedor_id=sobre.data.proveedor_id,
            id_mensaje=sobre.id,
        )
    )


def suscribirse_a_comandos(url_broker: str = PULSAR_URL):
    manejadores = {
        "AsignarProveedor": _al_asignar_proveedor,
        "LiberarProveedor": _al_liberar_proveedor,
    }
    ConsumidorBase(
        url_broker=url_broker,
        topico=TOPICO_COMANDOS,
        suscripcion=f"{SUSCRIPCION}-comandos",
        schema_sobre=ComandoMatching,
        manejadores=manejadores,
    ).iniciar()
