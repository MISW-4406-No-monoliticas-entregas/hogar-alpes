"""Objetos valor del módulo matching."""
from dataclasses import dataclass
from enum import Enum

from seedwork.dominio.objetos_valor import ObjetoValor


class EstadoAsignacion(str, Enum):
    ASIGNADA = "ASIGNADA"
    SIN_PROVEEDOR = "SIN_PROVEEDOR"
    LIBERADA = "LIBERADA"


@dataclass(frozen=True)
class Servicio(ObjetoValor):
    valor: str


@dataclass(frozen=True)
class Zona(ObjetoValor):
    valor: str
