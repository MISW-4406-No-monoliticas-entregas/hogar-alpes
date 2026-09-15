"""Comando LiberarProveedor y su handler.

Compensación que una saga futura usará para deshacer una asignación (hoy se
invoca a mano o por HTTP). Libera la asignación activa del siniestro y marca
el proveedor como disponible de nuevo. No publica evento de integración:
todavía no hay un tipo definido para ello, y la orquestación completa es de
una entrega futura.
"""
import uuid
from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando, ComandoHandler, ejecutar_comando
from seedwork.infraestructura.idempotencia import registrar_mensaje, MensajeDuplicado
from modulos.matching.dominio.excepciones import AsignacionNoExiste
from modulos.matching.aplicacion.servicios import (
    nueva_uow,
    repositorio_asignaciones_en,
    repositorio_proveedores_en,
)


@dataclass
class LiberarProveedor(Comando):
    id_siniestro: str
    proveedor_id: str
    id_mensaje: str | None = None  # id del mensaje del broker; None si viene por HTTP


class LiberarProveedorHandler(ComandoHandler):
    def handle(self, comando: LiberarProveedor) -> str | None:
        with nueva_uow() as uow:
            if comando.id_mensaje:
                try:
                    registrar_mensaje(uow.session, comando.id_mensaje)
                except MensajeDuplicado:
                    return None

            repo_asignaciones = repositorio_asignaciones_en(uow)
            repo_proveedores = repositorio_proveedores_en(uow)

            asignacion = repo_asignaciones.obtener_asignada_por_siniestro(comando.id_siniestro)
            if asignacion is None:
                raise AsignacionNoExiste(comando.id_siniestro)

            asignacion.liberar()
            repo_asignaciones.actualizar(asignacion)

            proveedor = repo_proveedores.obtener_por_id(uuid.UUID(comando.proveedor_id))
            if proveedor is not None:
                proveedor.marcar_disponible()
                repo_proveedores.actualizar(proveedor)

            uow.registrar_agregado(asignacion)
            uow.commit()
        return str(asignacion.id)


@ejecutar_comando.register(LiberarProveedor)
def _(comando: LiberarProveedor):
    return LiberarProveedorHandler().handle(comando)
