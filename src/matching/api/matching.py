"""Blueprint de la API HTTP del módulo matching."""
import dataclasses

from flask import Blueprint, request, jsonify

from seedwork.aplicacion.queries import ejecutar_query
from seedwork.presentacion.api import APIError
from modulos.matching.aplicacion.queries.listar_proveedores import (
    ListarProveedoresPorZonaYServicio,
)
from modulos.matching.aplicacion.queries.obtener_asignacion import (
    ObtenerAsignacionPorSiniestro,
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


@bp.get("/asignaciones/<id_siniestro>")
def obtener_asignacion(id_siniestro):
    # Consulta síncrona (permitida): estado de la asignación de un siniestro.
    resultado = ejecutar_query(
        ObtenerAsignacionPorSiniestro(id_siniestro=id_siniestro)
    ).resultado
    if resultado is None:
        raise APIError("No hay asignación para ese siniestro", 404)
    return jsonify(dataclasses.asdict(resultado)), 200
