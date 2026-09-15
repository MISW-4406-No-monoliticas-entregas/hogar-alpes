"""Comando AsignarProveedor y su handler."""
import uuid
from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando, ComandoHandler, ejecutar_comando
from seedwork.infraestructura.idempotencia import registrar_mensaje, MensajeDuplicado
from modulos.siniestros.dominio.excepciones import SiniestroNoExiste
from modulos.siniestros.aplicacion.servicios import nueva_uow, repositorio_en


@dataclass
class AsignarProveedor(Comando):
    id_siniestro: str
    proveedor_id: str
    id_mensaje: str | None = None  # id del mensaje del broker; None si viene por HTTP


class AsignarProveedorHandler(ComandoHandler):
    def handle(self, comando: AsignarProveedor) -> str | None:
        with nueva_uow() as uow:
            if comando.id_mensaje:
                try:
                    registrar_mensaje(uow.session, comando.id_mensaje)
                except MensajeDuplicado:
                    return None
            repo = repositorio_en(uow)
            siniestro = repo.obtener_por_id(uuid.UUID(comando.id_siniestro))
            if siniestro is None:
                raise SiniestroNoExiste(comando.id_siniestro)

            siniestro.asignar_proveedor(comando.proveedor_id)

            repo.actualizar(siniestro)
            uow.registrar_agregado(siniestro)
            uow.commit()
        return str(siniestro.id)


@ejecutar_comando.register(AsignarProveedor)
def _(comando: AsignarProveedor):
    return AsignarProveedorHandler().handle(comando)
