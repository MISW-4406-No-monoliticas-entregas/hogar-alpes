"""Suscriptor de solo-log a eventos.siniestros (S2).

Entrega parcial: S7 ya se entera de lo que pasa en Siniestros (demuestra que
los servicios se oyen entre sí), pero todavía sin lógica de negocio ni
orquestación — eso es de la saga que vendrá en una entrega futura. Por eso
solo registra en log y hace ack; no hay UoW, idempotencia ni efectos de
dominio aquí.
"""
import logging

from config.settings import PULSAR_URL, TOPICO_EVENTOS_SINIESTROS, SUSCRIPCION
from seedwork.infraestructura.consumidores import ConsumidorBase
from modulos.matching.infraestructura.schema.v1.eventos_siniestros import EventoSiniestros

logger = logging.getLogger(__name__)


def _loguear_evento(sobre):
    logger.info(
        "[eventos.siniestros] type=%s id_siniestro=%s data=%s",
        sobre.type, sobre.data.id_siniestro, sobre.data,
    )


def suscribirse_a_eventos_siniestros(url_broker: str = PULSAR_URL):
    manejadores = {
        "SiniestroRegistrado": _loguear_evento,
        "ProveedorAsignado": _loguear_evento,
    }
    ConsumidorBase(
        url_broker=url_broker,
        topico=TOPICO_EVENTOS_SINIESTROS,
        suscripcion=f"{SUSCRIPCION}-eventos-siniestros",
        schema_sobre=EventoSiniestros,
        manejadores=manejadores,
    ).iniciar()
