"""Handlers de eventos de dominio → comandos de compensación en Pulsar."""
from seedwork.aplicacion.eventos import suscribirse_a_evento
from modulos.orquestador.dominio.eventos import CompensacionIniciada
from modulos.orquestador.infraestructura.despachadores import DespachadorCompensaciones


def _al_iniciar_compensacion(evento: CompensacionIniciada, **kwargs):
    despachador = DespachadorCompensaciones()
    despachador.publicar_rechazar_siniestro(evento.siniestro_id, evento.motivo)
    if evento.proveedor_id:
        despachador.publicar_liberar_proveedor(evento.siniestro_id, evento.proveedor_id)


def registrar_handlers():
    suscribirse_a_evento(CompensacionIniciada, _al_iniciar_compensacion)
