"""Blueprint HTTP del servicio de Reglas de Partner.

Los GET son las consultas sincronas permitidas. El POST es una
utilidad de prueba para disparar el comando sin publicar en el topico, el camino
real de produccion es comandos.reglas.
"""
import dataclasses

from flask import Blueprint, jsonify, request

from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.queries import ejecutar_query
from seedwork.presentacion.api import APIError
from modulos.reglas.aplicacion.comandos.validar_siniestro import ValidarSiniestro
from modulos.reglas.aplicacion.queries.obtener_reglas_partner import ObtenerReglasDePartner
from modulos.reglas.aplicacion.queries.obtener_validaciones import (
    ObtenerValidacionesDePartner,
)

bp = Blueprint("reglas", __name__)


@bp.get("/partners/<partner_id>/reglas")
def obtener_reglas(partner_id):
    resultado = ejecutar_query(ObtenerReglasDePartner(partner_id=partner_id)).resultado
    if resultado is None:
        raise APIError("El partner no tiene reglas configuradas", 404)
    return jsonify(dataclasses.asdict(resultado)), 200


@bp.get("/partners/<partner_id>/validaciones")
def listar_validaciones(partner_id):
    limite = int(request.args.get("limite", 50))
    resultado = ejecutar_query(
        ObtenerValidacionesDePartner(partner_id=partner_id, limite=limite)
    ).resultado
    return jsonify([dataclasses.asdict(v) for v in resultado]), 200


@bp.post("/validaciones")
def validar():
    cuerpo = request.get_json(force=True, silent=True) or {}
    faltantes = [c for c in ("id_siniestro", "partner_id", "monto") if not cuerpo.get(c)]
    if faltantes:
        raise APIError(f"Faltan campos: {', '.join(faltantes)}", 400)
    id_validacion = ejecutar_comando(
        ValidarSiniestro(
            id_siniestro=cuerpo["id_siniestro"],
            partner_id=cuerpo["partner_id"],
            monto=float(cuerpo["monto"]),
            moneda=cuerpo.get("moneda", "COP"),
            servicio=cuerpo.get("servicio", ""),
            zona=cuerpo.get("zona", ""),
        )
    )
    return jsonify({"id_validacion": id_validacion}), 201
