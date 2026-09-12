"""Query ListarSincronizacionesPorPartner y su handler."""
from dataclasses import dataclass

from seedwork.aplicacion.queries import (
    Query,
    QueryHandler,
    QueryResultado,
    ejecutar_query,
)
from modulos.sincronizaciones.infraestructura import vistas


@dataclass
class ListarSincronizacionesPorPartner(Query):
    partner_id: str


class ListarSincronizacionesPorPartnerHandler(QueryHandler):
    def handle(self, query: ListarSincronizacionesPorPartner) -> QueryResultado:
        return QueryResultado(resultado=vistas.listar_por_partner(query.partner_id))


@ejecutar_query.register(ListarSincronizacionesPorPartner)
def _(query: ListarSincronizacionesPorPartner) -> QueryResultado:
    return ListarSincronizacionesPorPartnerHandler().handle(query)
