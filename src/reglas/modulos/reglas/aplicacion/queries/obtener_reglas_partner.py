"""Query ObtenerReglasDePartner (lado de lectura)."""
from dataclasses import dataclass

from seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado, ejecutar_query
from modulos.reglas.infraestructura import vistas


@dataclass
class ObtenerReglasDePartner(Query):
    partner_id: str


class ObtenerReglasDePartnerHandler(QueryHandler):
    def handle(self, query: ObtenerReglasDePartner) -> QueryResultado:
        return QueryResultado(resultado=vistas.obtener_reglas(query.partner_id))


@ejecutar_query.register(ObtenerReglasDePartner)
def _(query: ObtenerReglasDePartner) -> QueryResultado:
    return ObtenerReglasDePartnerHandler().handle(query)
