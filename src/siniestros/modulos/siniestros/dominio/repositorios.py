"""Interfaz del repositorio de siniestros (puerto de salida en el dominio)."""
import uuid
from abc import abstractmethod

from seedwork.dominio.repositorios import Repositorio
from modulos.siniestros.dominio.entidades import Siniestro


class RepositorioSiniestros(Repositorio):
    @abstractmethod
    def obtener_por_id(self, id: uuid.UUID) -> Siniestro | None:
        ...

    @abstractmethod
    def agregar(self, siniestro: Siniestro):
        ...

    @abstractmethod
    def actualizar(self, siniestro: Siniestro):
        ...
