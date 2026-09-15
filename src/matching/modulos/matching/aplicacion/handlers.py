"""Handlers de eventos de dominio → eventos de integración en Pulsar."""
from seedwork.aplicacion.eventos import suscribirse_a_evento
from modulos.matching.dominio.eventos import ProveedorAsignado, SinProveedorDisponible
from modulos.matching.infraestructura.despachadores import DespachadorEventos


def _al_asignar_proveedor(evento: ProveedorAsignado, **kwargs):
    DespachadorEventos().publicar_proveedor_asignado(evento)


def _al_sin_proveedor_disponible(evento: SinProveedorDisponible, **kwargs):
    DespachadorEventos().publicar_sin_proveedor_disponible(evento)


def registrar_handlers():
    suscribirse_a_evento(ProveedorAsignado, _al_asignar_proveedor)
    suscribirse_a_evento(SinProveedorDisponible, _al_sin_proveedor_disponible)
