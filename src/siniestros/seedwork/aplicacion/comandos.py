"""Comando base y mediador de comandos (singledispatch)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import singledispatch


@dataclass
class Comando:
    ...


class ComandoHandler(ABC):
    @abstractmethod
    def handle(self, comando: Comando):
        ...


@singledispatch
def ejecutar_comando(comando):
    raise NotImplementedError(
        f"No existe un handler registrado para el comando {type(comando).__name__}"
    )
