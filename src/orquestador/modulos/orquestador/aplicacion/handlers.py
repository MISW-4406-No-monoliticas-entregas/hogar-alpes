"""Handlers de eventos de dominio -> comandos publicados en Pulsar.

La Unidad de Trabajo despacha estos eventos DESPUES del commit, asi que cuando
se publica un comando hacia otro servicio el paso ya quedo persistido en el
Saga Log. Si el proceso muere entre el commit y la publicacion, la fila queda
en el paso anterior y se ve en la tabla, que es el limite conocido de no tener
outbox todavia.
"""
from seedwork.aplicacion.eventos import suscribirse_a_evento
from modulos.orquestador.dominio.eventos import (
    CompensacionIniciada,
    RegistroRequerido,
    ValidacionRequerida,
    AsignacionRequerida,
    SagaCompletada,
)
from modulos.orquestador.infraestructura.despachadores import (
    DespachadorCompensaciones,
    DespachadorPasosFelices,
)


def _al_iniciar_compensacion(evento: CompensacionIniciada, **kwargs):
    despachador = DespachadorCompensaciones()
    despachador.publicar_rechazar_siniestro(evento.siniestro_id, evento.motivo)
    if evento.proveedor_id:
        despachador.publicar_liberar_proveedor(evento.siniestro_id, evento.proveedor_id)


def _al_requerir_registro(evento: RegistroRequerido, **kwargs):
    DespachadorPasosFelices().publicar_registrar_siniestro(
        partner_id=evento.partner_id,
        poliza=evento.poliza,
        monto=evento.monto,
        moneda=evento.moneda,
        calle=evento.calle,
        ciudad=evento.ciudad,
        pais=evento.pais,
    )


def _al_requerir_validacion(evento: ValidacionRequerida, **kwargs):
    DespachadorPasosFelices().publicar_validar_siniestro(
        siniestro_id=evento.siniestro_id,
        partner_id=evento.partner_id,
        monto=evento.monto,
        moneda=evento.moneda,
        servicio=evento.servicio,
        zona=evento.zona,
    )


def _al_requerir_asignacion(evento: AsignacionRequerida, **kwargs):
    despachador = DespachadorPasosFelices()
    despachador.publicar_marcar_validado(evento.siniestro_id)
    despachador.publicar_asignar_proveedor(
        siniestro_id=evento.siniestro_id,
        servicio=evento.servicio,
        zona=evento.zona,
    )


def _al_completar_saga(evento: SagaCompletada, **kwargs):
    if evento.proveedor_id:
        DespachadorPasosFelices().publicar_proveedor_asignado_a_siniestros(
            evento.siniestro_id, evento.proveedor_id
        )


def registrar_handlers():
    suscribirse_a_evento(CompensacionIniciada, _al_iniciar_compensacion)
    suscribirse_a_evento(RegistroRequerido, _al_requerir_registro)
    suscribirse_a_evento(ValidacionRequerida, _al_requerir_validacion)
    suscribirse_a_evento(AsignacionRequerida, _al_requerir_asignacion)
    suscribirse_a_evento(SagaCompletada, _al_completar_saga)
