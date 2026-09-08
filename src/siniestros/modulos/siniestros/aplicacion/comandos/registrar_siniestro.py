"""Comando RegistrarSiniestro y su handler."""
from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando, ComandoHandler, ejecutar_comando
from modulos.siniestros.dominio.fabricas import FabricaSiniestro
from modulos.siniestros.aplicacion.dto import SiniestroDTO
from modulos.siniestros.aplicacion.mapeadores import MapeadorSiniestro
from modulos.siniestros.aplicacion.servicios import nueva_uow, repositorio_en


@dataclass
class RegistrarSiniestro(Comando):
    partner_id: str
    poliza: str
    monto: float
    moneda: str
    calle: str
    ciudad: str
    pais: str = "CO"


class RegistrarSiniestroHandler(ComandoHandler):
    def __init__(self):
        self.fabrica = FabricaSiniestro()
        self.mapeador = MapeadorSiniestro()

    def handle(self, comando: RegistrarSiniestro) -> str:
        dto = SiniestroDTO(
            partner_id=comando.partner_id,
            poliza=comando.poliza,
            monto=comando.monto,
            moneda=comando.moneda,
            calle=comando.calle,
            ciudad=comando.ciudad,
            pais=comando.pais,
        )
        valores = self.mapeador.dto_a_objetos_valor(dto)
        siniestro = self.fabrica.crear_siniestro(**valores)

        with nueva_uow() as uow:
            repositorio_en(uow).agregar(siniestro)
            uow.registrar_agregado(siniestro)
            uow.commit()
        return str(siniestro.id)


@ejecutar_comando.register(RegistrarSiniestro)
def _(comando: RegistrarSiniestro):
    return RegistrarSiniestroHandler().handle(comando)
