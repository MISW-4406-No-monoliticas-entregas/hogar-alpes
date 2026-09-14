"""Handlers del evento de dominio SiniestroSincronizado.

Dos suscriptores, ambos disparados por la UoW tras el commit:
  1. publica el COMANDO canónico RegistrarSiniestro en comandos.siniestros
     (S9 es productor del comando que consume S2).
  2. publica el EVENTO de integración SiniestroSincronizado en eventos.partners.
"""
from seedwork.aplicacion.eventos import suscribirse_a_evento
from modulos.sincronizaciones.dominio.eventos import SiniestroSincronizado
from modulos.sincronizaciones.infraestructura.despachadores import (
    DespachadorComandos,
    DespachadorEventos,
)


def _publicar_comando_registrar(evento: SiniestroSincronizado, **kwargs):
    DespachadorComandos().publicar_registrar_siniestro(evento)


def _publicar_evento_sincronizado(evento: SiniestroSincronizado, **kwargs):
    DespachadorEventos().publicar_siniestro_sincronizado(evento)


def registrar_handlers():
    suscribirse_a_evento(SiniestroSincronizado, _publicar_comando_registrar)
    suscribirse_a_evento(SiniestroSincronizado, _publicar_evento_sincronizado)
