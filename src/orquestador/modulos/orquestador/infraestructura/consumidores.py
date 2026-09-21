"""Consumidores del orquestador: tres suscripciones, una por servicio que
participa en la saga.

    eventos.siniestros  SiniestroRegistrado          -> vincula y pasa a VALIDANDO
    eventos.reglas      SiniestroAprobadoPorReglas   -> pasa a ASIGNANDO
                        SiniestroRechazadoPorReglas  -> compensa (D)
    eventos.matching    ProveedorAsignado            -> anota (D) y COMPLETADA
                        SinProveedorDisponible       -> compensa (D)

Usan el ConsumidorBase del seedwork (Key_Shared + ack tardio + nack), igual que
los otros 4 servicios, y cada handler es idempotente por el id del mensaje.

Cuando un mismo evento dispara dos comandos (ProveedorAsignado), el segundo usa
un id_mensaje derivado: si los dos registraran el mismo id, el segundo se veria
como duplicado y no correria.
"""
from config.settings import (
    PULSAR_URL,
    TOPICO_EVENTOS_SINIESTROS,
    TOPICO_EVENTOS_REGLAS,
    TOPICO_EVENTOS_MATCHING,
    SUSCRIPCION,
)
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.infraestructura.consumidores import ConsumidorBase
from modulos.orquestador.aplicacion.comandos.compensaciones import (
    CompensarSaga,
    RegistrarProveedorAsignado,
)
from modulos.orquestador.aplicacion.comandos.pasos_felices import (
    VincularSiniestro,
    AvanzarAAsignacion,
    CompletarSaga,
)
from modulos.orquestador.infraestructura.schema.v1.eventos_siniestros import (
    EventoSiniestros,
)
from modulos.orquestador.infraestructura.schema.v1.eventos_reglas import EventoReglas
from modulos.orquestador.infraestructura.schema.v1.eventos_matching import EventoMatching


def _al_siniestro_registrado(sobre):
    ejecutar_comando(
        VincularSiniestro(
            partner_id=sobre.data.partner_id,
            poliza=sobre.data.poliza,
            siniestro_id=sobre.data.id_siniestro,
            monto=sobre.data.monto,
            moneda=sobre.data.moneda or "COP",
            id_mensaje=sobre.id,
        )
    )


def suscribirse_a_eventos_siniestros(url_broker: str = PULSAR_URL):
    ConsumidorBase(
        url_broker=url_broker,
        topico=TOPICO_EVENTOS_SINIESTROS,
        suscripcion=f"{SUSCRIPCION}-eventos-siniestros",
        schema_sobre=EventoSiniestros,
        manejadores={"SiniestroRegistrado": _al_siniestro_registrado},
    ).iniciar()


def _al_siniestro_aprobado_por_reglas(sobre):
    ejecutar_comando(
        AvanzarAAsignacion(
            siniestro_id=sobre.data.id_siniestro,
            servicio=sobre.data.servicio,
            zona=sobre.data.zona,
            id_mensaje=sobre.id,
        )
    )


def _al_siniestro_rechazado_por_reglas(sobre):
    ejecutar_comando(
        CompensarSaga(
            siniestro_id=sobre.data.id_siniestro,
            motivo=f"Rechazado por reglas: {sobre.data.motivo}",
            id_mensaje=sobre.id,
        )
    )


def suscribirse_a_eventos_reglas(url_broker: str = PULSAR_URL):
    manejadores = {
        "SiniestroAprobadoPorReglas": _al_siniestro_aprobado_por_reglas,
        "SiniestroRechazadoPorReglas": _al_siniestro_rechazado_por_reglas,
    }
    ConsumidorBase(
        url_broker=url_broker,
        topico=TOPICO_EVENTOS_REGLAS,
        suscripcion=f"{SUSCRIPCION}-eventos-reglas",
        schema_sobre=EventoReglas,
        manejadores=manejadores,
    ).iniciar()


def _al_sin_proveedor_disponible(sobre):
    ejecutar_comando(
        CompensarSaga(
            siniestro_id=sobre.data.id_siniestro,
            motivo="Sin proveedor disponible para el servicio/zona solicitados",
            id_mensaje=sobre.id,
        )
    )


def _al_proveedor_asignado(sobre):
    ejecutar_comando(
        RegistrarProveedorAsignado(
            siniestro_id=sobre.data.id_siniestro,
            proveedor_id=sobre.data.proveedor_id,
            id_mensaje=sobre.id,
        )
    )
    ejecutar_comando(
        CompletarSaga(
            siniestro_id=sobre.data.id_siniestro,
            id_mensaje=f"{sobre.id}:completar" if sobre.id else None,
        )
    )


def suscribirse_a_eventos_matching(url_broker: str = PULSAR_URL):
    manejadores = {
        "SinProveedorDisponible": _al_sin_proveedor_disponible,
        "ProveedorAsignado": _al_proveedor_asignado,
    }
    ConsumidorBase(
        url_broker=url_broker,
        topico=TOPICO_EVENTOS_MATCHING,
        suscripcion=f"{SUSCRIPCION}-eventos-matching",
        schema_sobre=EventoMatching,
        manejadores=manejadores,
    ).iniciar()
