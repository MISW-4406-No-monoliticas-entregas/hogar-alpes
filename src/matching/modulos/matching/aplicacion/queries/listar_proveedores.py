"""Query ListarProveedoresPorZonaYServicio y su handler (lado de lectura)."""
from dataclasses import dataclass

from seedwork.aplicacion.queries import (
    Query,
    QueryHandler,
    QueryResultado,
    ejecutar_query,
)
from modulos.matching.infraestructura import vistas


@dataclass
class ListarProveedoresPorZonaYServicio(Query):
    zona: str
    servicio: str


class ListarProveedoresPorZonaYServicioHandler(QueryHandler):
    def handle(self, query: ListarProveedoresPorZonaYServicio) -> QueryResultado:
        resultado = vistas.listar_por_zona_servicio(query.zona, query.servicio)
        return QueryResultado(resultado=resultado)


@ejecutar_query.register(ListarProveedoresPorZonaYServicio)
def _(query: ListarProveedoresPorZonaYServicio) -> QueryResultado:
    return ListarProveedoresPorZonaYServicioHandler().handle(query)
