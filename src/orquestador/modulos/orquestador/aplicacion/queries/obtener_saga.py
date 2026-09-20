"""Query ObtenerSagaPorSiniestro y su handler (lado de lectura)."""
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
