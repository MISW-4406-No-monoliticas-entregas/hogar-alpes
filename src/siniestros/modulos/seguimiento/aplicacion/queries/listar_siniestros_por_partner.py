"""Query ListarSiniestrosPorPartner + handler (lado de lectura, CQS)."""
from dataclasses import dataclass

from seedwork.aplicacion.queries import (
    Query,
    QueryHandler,
    QueryResultado,
    ejecutar_query,
)
from modulos.seguimiento.infraestructura import vistas


@dataclass
class ListarSiniestrosPorPartner(Query):
    partner_id: str


class ListarSiniestrosPorPartnerHandler(QueryHandler):
    def handle(self, query: ListarSiniestrosPorPartner) -> QueryResultado:
        return QueryResultado(resultado=vistas.listar_por_partner(query.partner_id))


@ejecutar_query.register(ListarSiniestrosPorPartner)
def _(query: ListarSiniestrosPorPartner) -> QueryResultado:
    return ListarSiniestrosPorPartnerHandler().handle(query)
