"""Reglas de negocio como objetos."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ReglaNegocio(ABC):
    mensaje: str = "Se ha violado una regla de negocio"

    def __init__(self, mensaje: str = "Se ha violado una regla de negocio"):
        self.mensaje = mensaje

    @abstractmethod
    def es_valido(self) -> bool:
        ...

    def __str__(self) -> str:
        return f"{self.__class__.__name__} - {self.mensaje}"
