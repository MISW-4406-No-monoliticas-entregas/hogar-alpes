"""Consumidores del modulo reglas.

Dos suscripciones independientes:
  comandos.reglas   -> ejecuta ValidarSiniestro (trabajo de negocio)
  eventos.siniestros -> por ahora solo registra en log lo que emite S2, que es
                        lo que demuestra que los servicios se oyen entre si en
                        esta entrega parcial. En la Entrega 5 la saga reacciona.
"""
import logging

from config.settings import (
    PULSAR_URL,
    SUSCRIPCION,
    TOPICO_COMANDOS,
    TOPICO_EVENTOS_SINIESTROS,
)
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.infraestructura.consumidores import ConsumidorBase
from modulos.reglas.aplicacion.comandos.validar_siniestro import ValidarSiniestro
from modulos.reglas.infraestructura.schema.v1.comandos import ComandoReglas
from modulos.reglas.infraestructura.schema.v1.eventos_siniestros import EventoSiniestros

logger = logging.getLogger(__name__)


def _al_validar_siniestro(sobre):
    ejecutar_comando(
        ValidarSiniestro(
            id_siniestro=sobre.data.id_siniestro,
            partner_id=sobre.data.partner_id,
            monto=sobre.data.monto,
            moneda=sobre.data.moneda,
            servicio=sobre.data.servicio,
            zona=sobre.data.zona,
            id_mensaje=sobre.id,
        )
    )


def suscribirse_a_comandos(url_broker: str = PULSAR_URL):
    ConsumidorBase(
        url_broker=url_broker,
        topico=TOPICO_COMANDOS,
        suscripcion=f"{SUSCRIPCION}-comandos",
        schema_sobre=ComandoReglas,
        manejadores={"ValidarSiniestro": _al_validar_siniestro},
    ).iniciar()


def _registrar_en_log(sobre):
    logger.info(
        "[eventos.siniestros] type=%s id_siniestro=%s partner=%s estado=%s",
        sobre.type,
        sobre.data.id_siniestro,
        sobre.data.partner_id,
        sobre.data.estado,
    )


def suscribirse_a_eventos_de_siniestros(url_broker: str = PULSAR_URL):
    ConsumidorBase(
        url_broker=url_broker,
        topico=TOPICO_EVENTOS_SINIESTROS,
        suscripcion=f"{SUSCRIPCION}-eventos-siniestros",
        schema_sobre=EventoSiniestros,
        manejadores={
            "SiniestroRegistrado": _registrar_en_log,
            "ProveedorAsignado": _registrar_en_log,
        },
    ).iniciar()
