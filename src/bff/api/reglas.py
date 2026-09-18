"""Rutas de reglas de partner: todas contra S10 (dato propio de ese contexto)."""
from flask import Blueprint, jsonify, request

from api.errores import APIError
from clientes import s10

bp = Blueprint("reglas", __name__)


@bp.get("/reglas/<partner_id>")
def obtener_reglas(partner_id):
    respuesta = s10.obtener_reglas(partner_id)
    return jsonify(respuesta.cuerpo), respuesta.codigo


@bp.get("/reglas/<partner_id>/validaciones")
def listar_validaciones(partner_id):
    limite = request.args.get("limite")
    if limite is not None:
        if not limite.isdigit() or int(limite) <= 0:
            raise APIError("El parámetro 'limite' debe ser un entero positivo", 400)
        limite = int(limite)
    respuesta = s10.listar_validaciones(partner_id, limite)
    return jsonify(respuesta.cuerpo), respuesta.codigo
