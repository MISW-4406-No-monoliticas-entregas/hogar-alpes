"""Query ObtenerAsignacionPorSiniestro y su handler (lado de lectura).

Devuelve la asignación más reciente de un siniestro, en cualquier estado
(ASIGNADA, SIN_PROVEEDOR o LIBERADA) — a diferencia del repositorio de
dominio, que solo busca la activa (ASIGNADA) para el caso de uso de liberar.
"""
from dataclasses import dataclass

from seedwork.aplicacion.queries import (
    Query,
    QueryHandler,
    QueryResultado,
    ejecutar_query,
)
from modulos.matching.infraestructura import vistas


@dataclass
class ObtenerAsignacionPorSiniestro(Query):
    id_siniestro: str


class ObtenerAsignacionPorSiniestroHandler(QueryHandler):
    def handle(self, query: ObtenerAsignacionPorSiniestro) -> QueryResultado:
        resultado = vistas.obtener_asignacion_por_siniestro(query.id_siniestro)
        return QueryResultado(resultado=resultado)


@ejecutar_query.register(ObtenerAsignacionPorSiniestro)
def _(query: ObtenerAsignacionPorSiniestro) -> QueryResultado:
    return ObtenerAsignacionPorSiniestroHandler().handle(query)
