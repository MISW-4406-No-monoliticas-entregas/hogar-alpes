"""Handlers que traducen eventos de dominio a eventos de integración en Pulsar."""
from seedwork.aplicacion.eventos import suscribirse_a_evento
from modulos.siniestros.dominio.eventos import (
    SiniestroRegistrado,
    ProveedorAsignado,
)
from modulos.siniestros.infraestructura.despachadores import DespachadorEventos


def _al_registrar_siniestro(evento: SiniestroRegistrado, **kwargs):
    DespachadorEventos().publicar_siniestro_registrado(evento)


def _al_asignar_proveedor(evento: ProveedorAsignado, **kwargs):
    DespachadorEventos().publicar_proveedor_asignado(evento)


def registrar_handlers():
    suscribirse_a_evento(SiniestroRegistrado, _al_registrar_siniestro)
    suscribirse_a_evento(ProveedorAsignado, _al_asignar_proveedor)
