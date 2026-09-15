"""Comando AsignarProveedor y su handler.

Busca un proveedor disponible para (servicio, zona); si lo encuentra lo marca
ocupado y la asignación queda ASIGNADA (emite ProveedorAsignado); si no,
la asignación queda SIN_PROVEEDOR (emite SinProveedorDisponible). Un solo
handler sirve para las dos entradas (HTTP y broker): por broker trae
`id_mensaje` y el handler lo registra DENTRO de la misma UoW que el negocio
(idempotencia atómica).
"""
from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando, ComandoHandler, ejecutar_comando
from seedwork.infraestructura.idempotencia import registrar_mensaje, MensajeDuplicado
from modulos.matching.dominio.fabricas import FabricaAsignacion
from modulos.matching.dominio.objetos_valor import Servicio, Zona
from modulos.matching.aplicacion.servicios import (
    nueva_uow,
    repositorio_asignaciones_en,
    repositorio_proveedores_en,
)


@dataclass
class AsignarProveedor(Comando):
    id_siniestro: str
    servicio: str
    zona: str
    id_mensaje: str | None = None  # id del mensaje del broker; None si viene por HTTP


class AsignarProveedorHandler(ComandoHandler):
    def __init__(self):
        self.fabrica = FabricaAsignacion()

    def handle(self, comando: AsignarProveedor) -> str | None:
        with nueva_uow() as uow:
            if comando.id_mensaje:
                try:
                    registrar_mensaje(uow.session, comando.id_mensaje)
                except MensajeDuplicado:
                    return None  # ya procesado; el consumidor hará ack sin repetir

            repo_proveedores = repositorio_proveedores_en(uow)
            repo_asignaciones = repositorio_asignaciones_en(uow)

            proveedor = repo_proveedores.buscar_disponible(comando.servicio, comando.zona)
            asignacion = self.fabrica.crear_asignacion(
                id_siniestro=comando.id_siniestro,
                servicio=Servicio(comando.servicio),
                zona=Zona(comando.zona),
                proveedor=proveedor,
            )
            if proveedor is not None:
                proveedor.marcar_ocupado()
                repo_proveedores.actualizar(proveedor)

            repo_asignaciones.agregar(asignacion)
            uow.registrar_agregado(asignacion)
            uow.commit()
        return str(asignacion.id)


@ejecutar_comando.register(AsignarProveedor)
def _(comando: AsignarProveedor):
    return AsignarProveedorHandler().handle(comando)
