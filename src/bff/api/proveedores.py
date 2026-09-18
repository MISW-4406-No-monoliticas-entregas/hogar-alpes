"""Rutas de proveedores: contra S7 (dato propio de ese contexto)."""
from flask import Blueprint, jsonify, request

from api.errores import APIError
from clientes import s7

bp = Blueprint("proveedores", __name__)


@bp.get("/proveedores")
def listar_proveedores():
    zona = request.args.get("zona")
    servicio = request.args.get("servicio")
    if not zona or not servicio:
        raise APIError("Debes indicar los parámetros: zona, servicio", 400)
    respuesta = s7.listar_proveedores(zona, servicio)
    return jsonify(respuesta.cuerpo), respuesta.codigo
