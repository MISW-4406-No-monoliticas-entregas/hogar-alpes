"""Reglas de negocio como objetos.

Decisión de diseño: objetivamos cada regla de negocio en una clase para poder
probarla unitariamente de forma aislada y para que el agregado exprese sus
invariantes de forma declarativa (self.validar_regla(...)). Es la base del ítem
1 de la rúbrica (reglas de negocio) y facilita la sustentación.
"""
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
