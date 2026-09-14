"""Blueprint HTTP de S9. Única entrada HTTP externa del sistema (los partners son
sistemas externos; esto NO cuenta como llamado entre servicios)."""
import dataclasses

from flask import Blueprint, request, jsonify

from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.queries import ejecutar_query
from seedwork.presentacion.api import APIError
from modulos.sincronizaciones.aplicacion.comandos.sincronizar_siniestro import (
    SincronizarSiniestro,
)
from modulos.sincronizaciones.aplicacion.queries.obtener_sincronizacion import (
    ObtenerSincronizacion,
)
from modulos.sincronizaciones.aplicacion.queries.listar_sincronizaciones_por_partner import (
    ListarSincronizacionesPorPartner,
)
from modulos.sincronizaciones.aplicacion.traductores.base import ErrorTraduccion
from modulos.sincronizaciones.aplicacion.traductores.registro import PartnerDesconocido

bp = Blueprint("sincronizaciones", __name__)


@bp.post("/partners/<partner_id>/siniestros")
def sincronizar(partner_id):
    payload = request.get_json(force=True, silent=True)
    if not isinstance(payload, dict) or not payload:
        raise APIError("Cuerpo JSON del partner requerido", 400)
    try:
        resultado = ejecutar_comando(
            SincronizarSiniestro(partner_id=partner_id, payload=payload)
        )
    except PartnerDesconocido:
        raise APIError(f"Partner desconocido: {partner_id}", 400)
    except ErrorTraduccion as e:
        raise APIError(str(e), 400)

    if resultado.duplicada:
        # Idempotencia de negocio: ya se había recibido ese partner_id + id_externo.
        return jsonify({"estado": resultado.estado}), 409
    return jsonify(
        {"id_sincronizacion": resultado.id_sincronizacion, "estado": resultado.estado}
    ), 202


@bp.get("/sincronizaciones/<id_sincronizacion>")
def obtener(id_sincronizacion):
    resultado = ejecutar_query(
        ObtenerSincronizacion(id_sincronizacion=id_sincronizacion)
    ).resultado
    if resultado is None:
        raise APIError("Sincronización no encontrada", 404)
    return jsonify(dataclasses.asdict(resultado)), 200


@bp.get("/partners/<partner_id>/sincronizaciones")
def listar(partner_id):
    resultado = ejecutar_query(
        ListarSincronizacionesPorPartner(partner_id=partner_id)
    ).resultado
    return jsonify([dataclasses.asdict(r) for r in resultado]), 200
