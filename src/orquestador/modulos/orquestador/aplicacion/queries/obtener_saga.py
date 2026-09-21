"""Queries de lectura del Saga Log."""
from dataclasses import dataclass

from seedwork.aplicacion.queries import (
    Query,
    QueryHandler,
    QueryResultado,
    ejecutar_query,
)
from modulos.orquestador.infraestructura import vistas


@dataclass
class ObtenerSagaPorSiniestro(Query):
    siniestro_id: str


class ObtenerSagaPorSiniestroHandler(QueryHandler):
    def handle(self, query: ObtenerSagaPorSiniestro) -> QueryResultado:
        return QueryResultado(resultado=vistas.obtener_por_siniestro(query.siniestro_id))


@ejecutar_query.register(ObtenerSagaPorSiniestro)
def _(query: ObtenerSagaPorSiniestro) -> QueryResultado:
    return ObtenerSagaPorSiniestroHandler().handle(query)


@dataclass
class ObtenerSagaPorId(Query):
    id_saga: str


class ObtenerSagaPorIdHandler(QueryHandler):
    def handle(self, query: ObtenerSagaPorId) -> QueryResultado:
        return QueryResultado(resultado=vistas.obtener_por_id(query.id_saga))


@ejecutar_query.register(ObtenerSagaPorId)
def _(query: ObtenerSagaPorId) -> QueryResultado:
    return ObtenerSagaPorIdHandler().handle(query)


@dataclass
class ListarSagas(Query):
    limite: int = 50


class ListarSagasHandler(QueryHandler):
    def handle(self, query: ListarSagas) -> QueryResultado:
        return QueryResultado(resultado=vistas.listar(query.limite))


@ejecutar_query.register(ListarSagas)
def _(query: ListarSagas) -> QueryResultado:
    return ListarSagasHandler().handle(query)
