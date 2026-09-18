"""Salud del BFF y de sus dependencias.

`/salud/dependencias` sí le pega a varios servicios, pero es diagnóstico de
infraestructura (¿está arriba cada uno?), no arma ningún estado de negocio.
"""
from flask import Blueprint, jsonify

from clientes import todos
from clientes.errores import ErrorCliente, ServicioNoConfigurado

bp = Blueprint("salud", __name__)


@bp.get("/salud")
def salud():
    return jsonify({"estado": "ok", "servicio": "bff"}), 200


@bp.get("/salud/dependencias")
def salud_dependencias():
    reporte = {}
    for cliente in todos:
        try:
            cliente.get("/salud")
            reporte[cliente.nombre] = {"estado": "ok", "url": cliente.url_base}
        except ServicioNoConfigurado:
            reporte[cliente.nombre] = {"estado": "no_integrado", "url": None}
        except ErrorCliente as e:
            reporte[cliente.nombre] = {
                "estado": "caido",
                "url": cliente.url_base,
                "detalle": e.mensaje,
            }
    return jsonify(reporte), 200
