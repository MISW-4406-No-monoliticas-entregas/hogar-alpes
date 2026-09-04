"""Objetos valor del módulo siniestros.

Inmutables e identificados por su valor. Encapsulan invariantes simples de
formato/estructura; las reglas del agregado viven en reglas.py.
"""
from dataclasses import dataclass
from enum import Enum

from seedwork.dominio.objetos_valor import ObjetoValor


class EstadoSiniestro(str, Enum):
    """Estados del ciclo de vida. str+Enum para serializar directo a texto."""
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
    """Monto estimado del siniestro. La positividad se valida como regla de
    negocio del agregado, no aquí, para que el mensaje de error sea de dominio."""
    valor: float
    moneda: str = "COP"


@dataclass(frozen=True)
class Direccion(ObjetoValor):
    calle: str
    ciudad: str
    pais: str = "CO"
