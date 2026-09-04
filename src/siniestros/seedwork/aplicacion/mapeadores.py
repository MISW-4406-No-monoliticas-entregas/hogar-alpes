"""Mapeadores base (traducción entre representaciones)."""
from abc import ABC, abstractmethod


class Mapeador(ABC):
    """Traduce entre entidades de dominio y DTOs de aplicación."""

    @abstractmethod
    def entidad_a_dto(self, entidad):
        ...

    @abstractmethod
    def dto_a_entidad(self, dto):
        ...
