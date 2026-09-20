"""Fábrica del agregado Saga."""
from dataclasses import dataclass

from seedwork.dominio.fabricas import Fabrica
from modulos.orquestador.dominio.entidades import Saga


@dataclass
class FabricaSaga(Fabrica):
    def crear_objeto(self, obj, mapeador=None):
        raise NotImplementedError

    def iniciar_saga(self, siniestro_id: str) -> Saga:
        saga = Saga()
        saga.iniciar(siniestro_id)
        return saga
