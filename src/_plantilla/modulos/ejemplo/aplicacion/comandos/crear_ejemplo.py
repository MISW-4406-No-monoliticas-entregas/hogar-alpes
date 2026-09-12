"""Comando CrearEjemplo y su handler.

Un solo handler sirve para las dos entradas (HTTP y broker). Cuando el comando
llega por el broker trae `id_mensaje`; el handler lo registra DENTRO de la misma
UoW que el trabajo de negocio (idempotencia atómica). Por HTTP `id_mensaje` es
None y se omite.
"""
from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando, ComandoHandler, ejecutar_comando
from seedwork.infraestructura.idempotencia import registrar_mensaje, MensajeDuplicado
from modulos.ejemplo.dominio.fabricas import FabricaEjemplo
from modulos.ejemplo.dominio.objetos_valor import Nombre
from modulos.ejemplo.aplicacion.servicios import nueva_uow, repositorio_en


@dataclass
class CrearEjemplo(Comando):
    nombre: str
    id_mensaje: str | None = None  # id del mensaje del broker; None si viene por HTTP


class CrearEjemploHandler(ComandoHandler):
    def __init__(self):
        self.fabrica = FabricaEjemplo()

    def handle(self, comando: CrearEjemplo) -> str | None:
        ejemplo = self.fabrica.crear_ejemplo(Nombre(comando.nombre))
        with nueva_uow() as uow:
            if comando.id_mensaje:
                try:
                    registrar_mensaje(uow.session, comando.id_mensaje)
                except MensajeDuplicado:
                    return None  # ya procesado; el consumidor hará ack sin repetir
            repositorio_en(uow).agregar(ejemplo)
            uow.registrar_agregado(ejemplo)
            uow.commit()
        return str(ejemplo.id)


@ejecutar_comando.register(CrearEjemplo)
def _(comando: CrearEjemplo):
    return CrearEjemploHandler().handle(comando)
