"""Repositorios: interfaz (puerto) en el dominio.

Ítem 2 (hexagonal): la interfaz vive en el dominio y la implementación concreta
(SQLAlchemy/PostgreSQL) vive en infraestructura. El dominio depende de la
abstracción, nunca al revés.
"""
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
