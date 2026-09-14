"""Comando SincronizarSiniestro y su handler (ACL de entrada del dominio).

Flujo: resolver traductor por partner_id -> traducir a canónico -> validar ->
idempotencia de negocio (partner_id + id_externo) -> persistir Sincronizacion ->
al commit, la UoW despacha SiniestroSincronizado y sus handlers publican el
comando RegistrarSiniestro (comandos.siniestros) y el evento de integración
(eventos.partners).
"""
import dataclasses
from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando, ComandoHandler, ejecutar_comando
from modulos.sincronizaciones.dominio.fabricas import FabricaSincronizacion
from modulos.sincronizaciones.dominio.objetos_valor import EstadoSincronizacion
from modulos.sincronizaciones.aplicacion.traductores.registro import (
    registro_de_traductores,
)
from modulos.sincronizaciones.aplicacion.servicios import nueva_uow, repositorio_en


@dataclass
class ResultadoSincronizacion:
    id_sincronizacion: str
    estado: str
    duplicada: bool = False


@dataclass
class SincronizarSiniestro(Comando):
    partner_id: str
    payload: dict  # JSON crudo tal como lo envía el partner


class SincronizarSiniestroHandler(ComandoHandler):
    def __init__(self):
        self.fabrica = FabricaSincronizacion()

    def handle(self, comando: SincronizarSiniestro) -> ResultadoSincronizacion:
        # 1. Traducir el formato propio del partner al canónico (ACL).
        traductor = registro_de_traductores.resolver(comando.partner_id)
        canonico = traductor.traducir(comando.partner_id, comando.payload)

        # 2. Construir el agregado (estado RECIBIDA).
        sincro = self.fabrica.crear_sincronizacion(
            partner_id=canonico.partner_id, id_externo=canonico.id_externo
        )

        with nueva_uow() as uow:
            repo = repositorio_en(uow)
            # 3. Idempotencia de negocio: no publicar dos veces el mismo siniestro.
            if repo.existe(canonico.partner_id, canonico.id_externo):
                return ResultadoSincronizacion(
                    id_sincronizacion="",
                    estado=EstadoSincronizacion.DUPLICADA.value,
                    duplicada=True,
                )
            # 4. Pasar a PUBLICADA y emitir el evento de dominio.
            sincro.sincronizar(dataclasses.asdict(canonico))
            repo.agregar(sincro)
            uow.registrar_agregado(sincro)
            uow.commit()  # despacha SiniestroSincronizado -> handlers publican al broker

        return ResultadoSincronizacion(
            id_sincronizacion=str(sincro.id),
            estado=sincro.estado.value,
        )


@ejecutar_comando.register(SincronizarSiniestro)
def _(comando: SincronizarSiniestro):
    return SincronizarSiniestroHandler().handle(comando)
