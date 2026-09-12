"""Objetos valor del módulo ejemplo."""
from dataclasses import dataclass
from enum import Enum

from seedwork.dominio.objetos_valor import ObjetoValor


class EstadoEjemplo(str, Enum):
    CREADO = "CREADO"


@dataclass(frozen=True)
class Nombre(ObjetoValor):
    valor: str
