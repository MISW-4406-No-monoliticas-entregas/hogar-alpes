"""Rutas de siniestros: registro (S9), detalle (S2), estado de la transacción (S4).

A quién le pega cada ruta (ver README):
- POST /siniestros                 -> S9  (ACL de entrada; S9 publica el comando)
- GET  /sincronizaciones/<id>      -> S9  (¿S9 aceptó y publicó el registro?)
- GET  /siniestros/<id>            -> S2  (detalle del agregado, proyección)
- GET  /partners/<id>/siniestros   -> S2  (listado por partner, proyección)
- GET  /siniestros/<id>/estado     -> S4  (Saga Log: paso actual / completada / compensada)
- GET  /siniestros/<id>/asignacion -> S7  (asignación de proveedor de ese siniestro)

Ninguna ruta combina respuestas de varios servicios: el estado de la
transacción larga lo responde el orquestador, no se reconstruye aquí.
"""
from flask import Blueprint, jsonify, request

from api.errores import APIError
from clientes import orquestador, s2, s7, s9

bp = Blueprint("siniestros", __name__)


@bp.post("/siniestros")
def registrar_siniestro():
    """Registra un siniestro nuevo a través de S9.

    Cuerpo esperado:
        {"partner_id": "seguros-alpes", "siniestro": { ...formato propio del partner... }}

    `siniestro` se reenvía tal cual a POST /partners/<partner_id>/siniestros de
    S9: el BFF no traduce el formato del partner (eso es el ACL de S9).
    """
    cuerpo = request.get_json(force=True, silent=True)
    if not isinstance(cuerpo, dict):
        raise APIError("Cuerpo JSON requerido", 400)
    partner_id = cuerpo.get("partner_id")
    siniestro = cuerpo.get("siniestro")
    if not partner_id or not isinstance(partner_id, str):
        raise APIError("Falta el campo 'partner_id'", 400)
    if not isinstance(siniestro, dict) or not siniestro:
        raise APIError("Falta el objeto 'siniestro' con el payload del partner", 400)

    respuesta = s9.registrar_siniestro(partner_id, siniestro)
    return jsonify(respuesta.cuerpo), respuesta.codigo


@bp.get("/sincronizaciones/<id_sincronizacion>")
def obtener_sincronizacion(id_sincronizacion):
    respuesta = s9.obtener_sincronizacion(id_sincronizacion)
    return jsonify(respuesta.cuerpo), respuesta.codigo


@bp.get("/siniestros/<id_siniestro>")
def obtener_siniestro(id_siniestro):
    respuesta = s2.obtener_siniestro(id_siniestro)
    return jsonify(respuesta.cuerpo), respuesta.codigo


@bp.get("/partners/<partner_id>/siniestros")
def listar_siniestros_por_partner(partner_id):
    respuesta = s2.listar_siniestros_por_partner(partner_id)
    return jsonify(respuesta.cuerpo), respuesta.codigo


@bp.get("/siniestros/<id_siniestro>/estado")
def obtener_estado_transaccion(id_siniestro):
    """Estado de la transacción larga según el Saga Log del orquestador (S4).

    Mientras S4 no esté integrado (ORQUESTADOR_URL vacía) responde 501.
    """
    respuesta = orquestador.obtener_saga(id_siniestro)
    return jsonify(respuesta.cuerpo), respuesta.codigo


@bp.get("/siniestros/<id_siniestro>/asignacion")
def obtener_asignacion(id_siniestro):
    respuesta = s7.obtener_asignacion(id_siniestro)
    return jsonify(respuesta.cuerpo), respuesta.codigo
