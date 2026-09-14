"""Query ObtenerValidacionesDePartner (historial del lado de lectura)."""
from dataclasses import dataclass

from seedwork.aplicacion.queries import Query, QueryHandler, QueryResultado, ejecutar_query
from modulos.reglas.infraestructura import vistas


@dataclass
class ObtenerValidacionesDePartner(Query):
    partner_id: str
    limite: int = 50


class ObtenerValidacionesDePartnerHandler(QueryHandler):
    def handle(self, query: ObtenerValidacionesDePartner) -> QueryResultado:
        return QueryResultado(
            resultado=vistas.listar_validaciones(query.partner_id, query.limite)
        )


@ejecutar_query.register(ObtenerValidacionesDePartner)
def _(query: ObtenerValidacionesDePartner) -> QueryResultado:
    return ObtenerValidacionesDePartnerHandler().handle(query)
