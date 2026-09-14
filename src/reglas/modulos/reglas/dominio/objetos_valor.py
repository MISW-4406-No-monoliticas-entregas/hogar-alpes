"""Objetos valor del modulo reglas."""
from dataclasses import dataclass
from enum import Enum

from seedwork.dominio.objetos_valor import ObjetoValor


class ResultadoValidacion(str, Enum):
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


@dataclass(frozen=True)
class PartnerId(ObjetoValor):
    valor: str


@dataclass(frozen=True)
class Monto(ObjetoValor):
    valor: float
    moneda: str = "COP"


@dataclass(frozen=True)
class Servicio(ObjetoValor):
    nombre: str


@dataclass(frozen=True)
class Zona(ObjetoValor):
    nombre: str


@dataclass(frozen=True)
class Evaluacion(ObjetoValor):
    """Veredicto del agregado ReglaDePartner sobre un siniestro."""
    resultado: ResultadoValidacion
    motivo: str
