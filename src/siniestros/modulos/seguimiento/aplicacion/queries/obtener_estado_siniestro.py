"""Query ObtenerEstadoSiniestro + handler (lado de lectura, CQS)."""
from dataclasses import dataclass

from seedwork.aplicacion.queries import (
    Query,
    QueryHandler,
    QueryResultado,
    ejecutar_query,
)
from modulos.seguimiento.infraestructura import vistas


@dataclass
class ObtenerEstadoSiniestro(Query):
    id_siniestro: str


class ObtenerEstadoSiniestroHandler(QueryHandler):
    def handle(self, query: ObtenerEstadoSiniestro) -> QueryResultado:
        return QueryResultado(resultado=vistas.obtener_estado(query.id_siniestro))


@ejecutar_query.register(ObtenerEstadoSiniestro)
def _(query: ObtenerEstadoSiniestro) -> QueryResultado:
    return ObtenerEstadoSiniestroHandler().handle(query)
