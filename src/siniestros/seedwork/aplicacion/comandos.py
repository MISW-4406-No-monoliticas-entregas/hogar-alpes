"""Comandos y su mediador (patrón CQS, lado de escritura).

El mediador usa functools.singledispatch: cada comando concreto registra su
handler y ejecutar_comando(comando) despacha al handler correcto por tipo.
Igual que en los tutoriales del curso.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import singledispatch


@dataclass
class Comando:
    """Marca un mensaje de intención de cambio de estado (imperativo)."""
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
