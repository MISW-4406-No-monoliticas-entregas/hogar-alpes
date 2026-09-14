"""Blueprint de la API HTTP del módulo matching."""
import dataclasses

from flask import Blueprint, request, jsonify

from seedwork.aplicacion.queries import ejecutar_query
from seedwork.presentacion.api import APIError
from modulos.matching.aplicacion.queries.listar_proveedores import (
    ListarProveedoresPorZonaYServicio,
)

bp = Blueprint("matching", __name__)


@bp.get("/proveedores")
def listar_proveedores():
    # Consulta síncrona (permitida): proveedores habilitados por zona y servicio.
    zona = request.args.get("zona")
    servicio = request.args.get("servicio")
    if not zona or not servicio:
        raise APIError("Debes indicar los parámetros: zona, servicio", 400)
    resultado = ejecutar_query(
        ListarProveedoresPorZonaYServicio(zona=zona, servicio=servicio)
    ).resultado
    return jsonify([dataclasses.asdict(p) for p in resultado]), 200
