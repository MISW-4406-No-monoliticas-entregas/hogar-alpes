"""Query ObtenerEjemplo y su handler (lado de lectura)."""
from dataclasses import dataclass

from seedwork.aplicacion.queries import (
    Query,
    QueryHandler,
    QueryResultado,
    ejecutar_query,
)
from modulos.ejemplo.infraestructura import vistas


@dataclass
class ObtenerEjemplo(Query):
    id_ejemplo: str


class ObtenerEjemploHandler(QueryHandler):
    def handle(self, query: ObtenerEjemplo) -> QueryResultado:
        return QueryResultado(resultado=vistas.obtener(query.id_ejemplo))


@ejecutar_query.register(ObtenerEjemplo)
def _(query: ObtenerEjemplo) -> QueryResultado:
    return ObtenerEjemploHandler().handle(query)
