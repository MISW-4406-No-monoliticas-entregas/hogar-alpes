"""Objetos valor base.

Un ObjetoValor es inmutable y su identidad es su valor (no tiene id). Se modela
con dataclass(frozen=True) para obtener inmutabilidad e igualdad estructural.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ObjetoValor:
    ...
