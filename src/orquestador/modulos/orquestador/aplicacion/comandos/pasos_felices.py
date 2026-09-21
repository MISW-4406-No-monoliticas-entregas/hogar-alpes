"""Camino feliz del orquestador (C). Archivo separado de compensaciones.py (D)
para minimizar conflictos de merge en la rama compartida feat/s4-orquestador.

Cuatro comandos, uno por paso de la transaccion larga:

    IniciarSaga          POST /sagas          -> publica RegistrarSiniestro (S2)
    VincularSiniestro    SiniestroRegistrado  -> publica ValidarSiniestro (S10)
    AvanzarAAsignacion   SiniestroAprobado... -> publica AsignarProveedor (S7)
    CompletarSaga        ProveedorAsignado    -> cierra la saga en COMPLETADA

Ninguno publica en Pulsar directamente: cada avance emite un evento de dominio
y la Unidad de Trabajo lo despacha despues del commit (ver aplicacion/handlers).
Asi el estado queda persistido antes de pedirle nada al servicio que sigue.

Los comandos que entran por un topico traen `id_mensaje` y lo registran dentro
de la misma Unidad de Trabajo que el trabajo de negocio: una reentrega de
Pulsar no avanza la saga dos veces.
"""
import logging
from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando, ComandoHandler, ejecutar_comando
from seedwork.infraestructura.idempotencia import registrar_mensaje, MensajeDuplicado
from modulos.orquestador.dominio.fabricas import FabricaSaga
from modulos.orquestador.aplicacion.servicios import nueva_uow, repositorio_sagas_en

logger = logging.getLogger(__name__)


@dataclass
class IniciarSaga(Comando):
    partner_id: str
    poliza: str
    monto: float
    servicio: str
    zona: str
    moneda: str = "COP"
    calle: str = ""
    ciudad: str = ""
    pais: str = "CO"


class IniciarSagaHandler(ComandoHandler):
    def __init__(self):
        self.fabrica = FabricaSaga()

    def handle(self, comando: IniciarSaga) -> str:
        with nueva_uow() as uow:
            saga = self.fabrica.iniciar_saga_pendiente(
                partner_id=comando.partner_id,
                poliza=comando.poliza,
                servicio=comando.servicio,
                zona=comando.zona,
                monto=comando.monto,
                moneda=comando.moneda,
                calle=comando.calle,
                ciudad=comando.ciudad,
                pais=comando.pais,
            )
            repositorio_sagas_en(uow).agregar(saga)
            uow.registrar_agregado(saga)
            uow.commit()
        return str(saga.id)


@ejecutar_comando.register(IniciarSaga)
def _(comando: IniciarSaga):
    return IniciarSagaHandler().handle(comando)


@dataclass
class VincularSiniestro(Comando):
    partner_id: str
    poliza: str
    siniestro_id: str
    monto: float = 0.0
    moneda: str = "COP"
    id_mensaje: str | None = None


class VincularSiniestroHandler(ComandoHandler):
    """S2 aviso que registro el siniestro.

    La saga se correlaciona por (partner_id, poliza) porque el evento
    SiniestroRegistrado no transporta ninguna referencia a la saga y el
    id_siniestro lo genera S2. Si no hay saga pendiente, este siniestro no
    lo inicio el orquestador (por ejemplo entro directo por S9) y no se toca.

    Dos transacciones a proposito, igual que la compensacion de D: la primera
    deja la fila en INICIADA y la segunda en VALIDANDO. Asi una consulta al
    Saga Log en el punto intermedio ve el paso de verdad, no un salto.
    """

    def handle(self, comando: VincularSiniestro) -> str | None:
        with nueva_uow() as uow:
            if comando.id_mensaje:
                try:
                    registrar_mensaje(uow.session, comando.id_mensaje)
                except MensajeDuplicado:
                    return None

            repo = repositorio_sagas_en(uow)
            saga = repo.obtener_pendiente(comando.partner_id, comando.poliza)
            if saga is None:
                logger.info(
                    "SiniestroRegistrado sin saga pendiente (partner=%s poliza=%s); se ignora",
                    comando.partner_id, comando.poliza,
                )
                uow.commit()
                return None

            saga.vincular_siniestro(comando.siniestro_id)
            repo.actualizar(saga)
            uow.registrar_agregado(saga)
            uow.commit()

        id_saga = saga.id

        with nueva_uow() as uow:
            repo = repositorio_sagas_en(uow)
            saga_actualizada = repo.obtener_por_id(id_saga)
            saga_actualizada.avanzar_a_validando(comando.monto, comando.moneda)
            repo.actualizar(saga_actualizada)
            uow.registrar_agregado(saga_actualizada)
            uow.commit()

        return str(id_saga)


@ejecutar_comando.register(VincularSiniestro)
def _(comando: VincularSiniestro):
    return VincularSiniestroHandler().handle(comando)


@dataclass
class AvanzarAAsignacion(Comando):
    siniestro_id: str
    servicio: str = ""
    zona: str = ""
    id_mensaje: str | None = None


class AvanzarAAsignacionHandler(ComandoHandler):
    """S10 aprobo las reglas del partner: toca pedirle proveedor a S7."""

    def handle(self, comando: AvanzarAAsignacion) -> str | None:
        with nueva_uow() as uow:
            if comando.id_mensaje:
                try:
                    registrar_mensaje(uow.session, comando.id_mensaje)
                except MensajeDuplicado:
                    return None

            repo = repositorio_sagas_en(uow)
            saga = repo.obtener_por_siniestro(comando.siniestro_id)
            if saga is None:
                logger.info(
                    "SiniestroAprobadoPorReglas sin saga (siniestro=%s); se ignora",
                    comando.siniestro_id,
                )
                uow.commit()
                return None

            saga.avanzar_a_asignando(comando.servicio, comando.zona)
            repo.actualizar(saga)
            uow.registrar_agregado(saga)
            uow.commit()
        return str(saga.id)


@ejecutar_comando.register(AvanzarAAsignacion)
def _(comando: AvanzarAAsignacion):
    return AvanzarAAsignacionHandler().handle(comando)


@dataclass
class CompletarSaga(Comando):
    siniestro_id: str
    id_mensaje: str | None = None


class CompletarSagaHandler(ComandoHandler):
    """S7 reservo proveedor: la transaccion larga cierra bien.

    Corre despues de RegistrarProveedorAsignado (el bookkeeping de D), que ya
    dejo anotado el proveedor_id en la fila.
    """

    def handle(self, comando: CompletarSaga) -> str | None:
        with nueva_uow() as uow:
            if comando.id_mensaje:
                try:
                    registrar_mensaje(uow.session, comando.id_mensaje)
                except MensajeDuplicado:
                    return None

            repo = repositorio_sagas_en(uow)
            saga = repo.obtener_por_siniestro(comando.siniestro_id)
            if saga is None:
                logger.info(
                    "ProveedorAsignado sin saga (siniestro=%s); se ignora",
                    comando.siniestro_id,
                )
                uow.commit()
                return None

            saga.completar()
            repo.actualizar(saga)
            uow.registrar_agregado(saga)
            uow.commit()
        return str(saga.id)


@ejecutar_comando.register(CompletarSaga)
def _(comando: CompletarSaga):
    return CompletarSagaHandler().handle(comando)
