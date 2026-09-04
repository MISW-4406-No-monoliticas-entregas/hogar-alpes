"""Handlers de seguimiento: reaccionan a eventos de dominio y proyectan.

Se suscriben POR NOMBRE de evento ("SiniestroRegistrado", "ProveedorAsignado")
para no importar ninguna clase del módulo siniestros (ítem 4). Leen los atributos
del evento por duck typing y actualizan la proyección estado_siniestro.

Importar este módulo registra las suscripciones (efecto de import).
"""
from seedwork.aplicacion.eventos import suscribirse_a_evento
from modulos.seguimiento.infraestructura.repositorios import (
    RepositorioEstadoSiniestro,
)

_repositorio = RepositorioEstadoSiniestro()


def _al_registrar_siniestro(evento, **kwargs):
    _repositorio.registrar_o_actualizar(
        id_siniestro=str(evento.id_siniestro),
        partner_id=evento.partner_id,
        estado=evento.estado,
        poliza=evento.poliza,
        monto=evento.monto,
        moneda=evento.moneda,
    )


def _al_asignar_proveedor(evento, **kwargs):
    _repositorio.registrar_o_actualizar(
        id_siniestro=str(evento.id_siniestro),
        estado=evento.estado,
        proveedor_id=evento.proveedor_id,
    )


def registrar_handlers():
    """Suscribe por nombre de evento; seguimiento no conoce las clases de siniestros."""
    suscribirse_a_evento("SiniestroRegistrado", _al_registrar_siniestro)
    suscribirse_a_evento("ProveedorAsignado", _al_asignar_proveedor)
