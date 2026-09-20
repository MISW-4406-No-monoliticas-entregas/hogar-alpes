"""Camino de fallo del orquestador (D). Archivo separado de pasos_felices.py
(C) para minimizar conflictos de merge en la rama compartida feat/s4-orquestador.

Dos comandos:
  - `RegistrarProveedorAsignado`: bookkeeping cuando S7 confirma una reserva
    (evento ProveedorAsignado) -- anota `proveedor_id` en la saga sin tocar
    su paso/estado, para saber qué liberar si algo falla después.
  - `CompensarSaga`: reacciona a cualquier fallo del camino feliz
    (SiniestroRechazadoPorReglas de S10, SinProveedorDisponible de S7, o
    cualquier otro que dispare C) publicando RechazarSiniestro siempre y
    LiberarProveedor solo si la saga ya tenía un proveedor reservado.

Ambos comandos crean la fila de la saga si no existe todavía (por ejemplo,
probando este módulo de forma aislada sin que el camino feliz de C esté
integrado), para no perder el registro.
"""
from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando, ComandoHandler, ejecutar_comando
from seedwork.infraestructura.idempotencia import registrar_mensaje, MensajeDuplicado
from modulos.orquestador.dominio.fabricas import FabricaSaga
from modulos.orquestador.aplicacion.servicios import nueva_uow, repositorio_sagas_en


def _obtener_o_iniciar_saga(repo, fabrica, siniestro_id: str):
    saga = repo.obtener_por_siniestro(siniestro_id)
    if saga is None:
        saga = fabrica.iniciar_saga(siniestro_id)
        repo.agregar(saga)
    return saga


@dataclass
class RegistrarProveedorAsignado(Comando):
    siniestro_id: str
    proveedor_id: str
    id_mensaje: str | None = None


class RegistrarProveedorAsignadoHandler(ComandoHandler):
    def __init__(self):
        self.fabrica = FabricaSaga()

    def handle(self, comando: RegistrarProveedorAsignado) -> str | None:
        with nueva_uow() as uow:
            if comando.id_mensaje:
                try:
                    registrar_mensaje(uow.session, comando.id_mensaje)
                except MensajeDuplicado:
                    return None

            repo = repositorio_sagas_en(uow)
            saga = _obtener_o_iniciar_saga(repo, self.fabrica, comando.siniestro_id)
            saga.registrar_proveedor_reservado(comando.proveedor_id)
            repo.actualizar(saga)

            uow.registrar_agregado(saga)
            uow.commit()
        return str(saga.id)


@ejecutar_comando.register(RegistrarProveedorAsignado)
def _(comando: RegistrarProveedorAsignado):
    return RegistrarProveedorAsignadoHandler().handle(comando)


@dataclass
class CompensarSaga(Comando):
    siniestro_id: str
    motivo: str
    id_mensaje: str | None = None


class CompensarSagaHandler(ComandoHandler):
    def __init__(self):
        self.fabrica = FabricaSaga()

    def handle(self, comando: CompensarSaga) -> str | None:
        # Paso 1: marcar COMPENSANDO. El commit dispara CompensacionIniciada,
        # que el despachador traduce en RechazarSiniestro (siempre) y
        # LiberarProveedor (si corresponde) -- ver aplicacion/handlers.py.
        with nueva_uow() as uow:
            if comando.id_mensaje:
                try:
                    registrar_mensaje(uow.session, comando.id_mensaje)
                except MensajeDuplicado:
                    return None

            repo = repositorio_sagas_en(uow)
            saga = _obtener_o_iniciar_saga(repo, self.fabrica, comando.siniestro_id)
            saga.compensar(comando.motivo)
            repo.actualizar(saga)

            uow.registrar_agregado(saga)
            uow.commit()

        id_saga = saga.id

        # Paso 2: ya se publicaron las compensaciones (fire-and-forget, sin
        # esperar confirmación de S2/S7); se cierra el camino de fallo.
        with nueva_uow() as uow:
            repo = repositorio_sagas_en(uow)
            saga_actualizada = repo.obtener_por_id(id_saga)
            saga_actualizada.completar_compensacion()
            repo.actualizar(saga_actualizada)
            uow.registrar_agregado(saga_actualizada)
            uow.commit()

        return str(id_saga)


@ejecutar_comando.register(CompensarSaga)
def _(comando: CompensarSaga):
    return CompensarSagaHandler().handle(comando)
