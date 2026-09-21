"""Consumidores de eventos.reglas y eventos.matching: el orquestador
reacciona a los dos fallos del camino feliz que le tocan a D, y registra de
verdad lo que S7 confirma (ya no es un script de prueba invocado a mano).

Usa el ConsumidorBase del seedwork (Key_Shared + ack tardío + nack), igual
que los otros 4 servicios. Nadie los arranca todavía desde un main.py -- eso
es ensamblar el servicio completo, fuera del alcance de este slice (ver
README). Quedan listos para que quien lo arme los conecte igual que a los
demás consumidores.
"""
from config.settings import (
    PULSAR_URL,
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
from modulos.orquestador.infraestructura.schema.v1.eventos_reglas import EventoReglas
from modulos.orquestador.infraestructura.schema.v1.eventos_matching import EventoMatching


def _al_siniestro_rechazado_por_reglas(sobre):
    ejecutar_comando(
        CompensarSaga(
            siniestro_id=sobre.data.id_siniestro,
            motivo=f"Rechazado por reglas: {sobre.data.motivo}",
            id_mensaje=sobre.id,
        )
    )


def suscribirse_a_eventos_reglas(url_broker: str = PULSAR_URL):
    manejadores = {"SiniestroRechazadoPorReglas": _al_siniestro_rechazado_por_reglas}
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
