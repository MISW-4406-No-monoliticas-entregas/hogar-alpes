"""Handlers de eventos de dominio del módulo siniestros.

Se suscriben (por señales) a los eventos de dominio y los traducen a eventos de
INTEGRACIÓN que se publican en Pulsar (tópico eventos.trabajos) para el resto de
la arquitectura. Esto convive con la actualización de la proyección que hace
seguimiento: ambos reaccionan al mismo evento de dominio, desacoplados.

Importar este módulo registra las suscripciones (efecto de import).
"""
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
