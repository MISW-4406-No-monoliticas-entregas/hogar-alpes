"""Traductor base y errores del ACL de entrada."""
from abc import ABC, abstractmethod

from modulos.sincronizaciones.aplicacion.dto import SiniestroCanonico


class ErrorTraduccion(Exception):
    """El payload del partner no pudo traducirse al modelo canónico."""


class Traductor(ABC):
    """Puerto del Anti-Corruption Layer: JSON propio del partner -> canónico."""

    @abstractmethod
    def traducir(self, partner_id: str, payload: dict) -> SiniestroCanonico:
        ...
