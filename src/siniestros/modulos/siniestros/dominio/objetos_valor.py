"""Objetos valor del módulo siniestros."""
from dataclasses import dataclass
from enum import Enum

from seedwork.dominio.objetos_valor import ObjetoValor


class EstadoSiniestro(str, Enum):
    REGISTRADO = "REGISTRADO"
    ASIGNADO = "ASIGNADO"


@dataclass(frozen=True)
class PartnerId(ObjetoValor):
    valor: str


@dataclass(frozen=True)
class Poliza(ObjetoValor):
    numero: str


@dataclass(frozen=True)
class Monto(ObjetoValor):
    valor: float
    moneda: str = "COP"


@dataclass(frozen=True)
class Direccion(ObjetoValor):
    calle: str
    ciudad: str
    pais: str = "CO"
