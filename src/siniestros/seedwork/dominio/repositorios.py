"""Interfaz base de repositorio."""
import uuid
from abc import ABC, abstractmethod


class Repositorio(ABC):
    @abstractmethod
    def obtener_por_id(self, id: uuid.UUID):
        ...

    @abstractmethod
    def agregar(self, entidad):
        ...

    @abstractmethod
    def actualizar(self, entidad):
        ...
