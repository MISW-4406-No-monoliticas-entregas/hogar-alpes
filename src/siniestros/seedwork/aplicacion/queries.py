"""Consultas y su mediador (patrón CQS, lado de lectura).

Las queries NO modifican estado: leen la proyección del módulo seguimiento.
Se despachan por tipo con singledispatch, simétrico a los comandos.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import singledispatch
from typing import Any


@dataclass
class Query:
    ...


@dataclass
class QueryResultado:
    resultado: Any = field(default=None)


class QueryHandler(ABC):
    @abstractmethod
    def handle(self, query: Query) -> QueryResultado:
        ...


@singledispatch
def ejecutar_query(query) -> QueryResultado:
    raise NotImplementedError(
        f"No existe un handler registrado para la query {type(query).__name__}"
    )
