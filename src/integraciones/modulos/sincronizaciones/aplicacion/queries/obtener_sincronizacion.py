"""Query ObtenerSincronizacion y su handler (lado de lectura)."""
from dataclasses import dataclass

from seedwork.aplicacion.queries import (
    Query,
    QueryHandler,
    QueryResultado,
    ejecutar_query,
)
from modulos.sincronizaciones.infraestructura import vistas


@dataclass
class ObtenerSincronizacion(Query):
    id_sincronizacion: str


class ObtenerSincronizacionHandler(QueryHandler):
    def handle(self, query: ObtenerSincronizacion) -> QueryResultado:
        return QueryResultado(resultado=vistas.obtener(query.id_sincronizacion))


@ejecutar_query.register(ObtenerSincronizacion)
def _(query: ObtenerSincronizacion) -> QueryResultado:
    return ObtenerSincronizacionHandler().handle(query)
