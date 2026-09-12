"""Handlers de eventos de dominio → eventos de integración en Pulsar."""
from seedwork.aplicacion.eventos import suscribirse_a_evento
from modulos.ejemplo.dominio.eventos import EjemploCreado
from modulos.ejemplo.infraestructura.despachadores import DespachadorEventos


def _al_crear_ejemplo(evento: EjemploCreado, **kwargs):
    DespachadorEventos().publicar_ejemplo_creado(evento)


def registrar_handlers():
    suscribirse_a_evento(EjemploCreado, _al_crear_ejemplo)
