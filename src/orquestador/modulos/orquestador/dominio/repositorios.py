"""Interfaz del repositorio del Saga Log (puerto de salida en el dominio)."""
import uuid
from abc import abstractmethod

from seedwork.dominio.repositorios import Repositorio
from modulos.orquestador.dominio.entidades import Saga


class RepositorioSagas(Repositorio):
    @abstractmethod
    def obtener_por_id(self, id: uuid.UUID) -> Saga | None:
        ...

    @abstractmethod
    def obtener_por_siniestro(self, siniestro_id: str) -> Saga | None:
        ...

    @abstractmethod
    def agregar(self, saga: Saga):
        ...

    @abstractmethod
    def actualizar(self, saga: Saga):
        ...
