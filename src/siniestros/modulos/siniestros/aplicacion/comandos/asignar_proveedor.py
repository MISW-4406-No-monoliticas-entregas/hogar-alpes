"""Comando AsignarProveedor + su handler (lado de escritura, CQS)."""
import uuid
from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando, ComandoHandler, ejecutar_comando
from modulos.siniestros.dominio.excepciones import SiniestroNoExiste
from modulos.siniestros.aplicacion.servicios import nueva_uow, repositorio_en


@dataclass
class AsignarProveedor(Comando):
    id_siniestro: str
    proveedor_id: str


class AsignarProveedorHandler(ComandoHandler):
    def handle(self, comando: AsignarProveedor) -> str:
        with nueva_uow() as uow:
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
