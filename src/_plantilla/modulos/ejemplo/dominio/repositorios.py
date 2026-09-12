"""Interfaz del repositorio de ejemplos (puerto de salida en el dominio)."""
import uuid
from abc import abstractmethod

from seedwork.dominio.repositorios import Repositorio
from modulos.ejemplo.dominio.entidades import Ejemplo


class RepositorioEjemplos(Repositorio):
    @abstractmethod
    def obtener_por_id(self, id: uuid.UUID) -> Ejemplo | None:
        ...

    @abstractmethod
    def agregar(self, ejemplo: Ejemplo):
        ...

    @abstractmethod
    def actualizar(self, ejemplo: Ejemplo):
        ...
