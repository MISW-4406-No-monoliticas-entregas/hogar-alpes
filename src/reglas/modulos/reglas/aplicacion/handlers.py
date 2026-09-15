"""Handlers de eventos de dominio que publican los eventos de integracion."""
from seedwork.aplicacion.eventos import suscribirse_a_evento
from modulos.reglas.dominio.eventos import (
    SiniestroAprobadoPorReglas,
    SiniestroRechazadoPorReglas,
)
from modulos.reglas.infraestructura.despachadores import DespachadorEventos


def _al_aprobar(evento: SiniestroAprobadoPorReglas, **kwargs):
    DespachadorEventos().publicar_siniestro_aprobado(evento)


def _al_rechazar(evento: SiniestroRechazadoPorReglas, **kwargs):
    DespachadorEventos().publicar_siniestro_rechazado(evento)


def registrar_handlers():
    suscribirse_a_evento(SiniestroAprobadoPorReglas, _al_aprobar)
    suscribirse_a_evento(SiniestroRechazadoPorReglas, _al_rechazar)
