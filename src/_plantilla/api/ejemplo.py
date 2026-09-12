"""Blueprint de la API HTTP del módulo ejemplo."""
import dataclasses

from flask import Blueprint, request, jsonify

from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.queries import ejecutar_query
from seedwork.presentacion.api import APIError
from modulos.ejemplo.aplicacion.comandos.crear_ejemplo import CrearEjemplo
from modulos.ejemplo.aplicacion.queries.obtener_ejemplo import ObtenerEjemplo

bp = Blueprint("ejemplo", __name__)


@bp.post("/ejemplos")
def crear_ejemplo():
    # Entrada HTTP de demo (sin id_mensaje: la idempotencia solo aplica al broker).
    cuerpo = request.get_json(force=True, silent=True) or {}
    if not cuerpo.get("nombre"):
        raise APIError("Falta el campo: nombre", 400)
    id_ejemplo = ejecutar_comando(CrearEjemplo(nombre=cuerpo["nombre"]))
    return jsonify({"id": id_ejemplo, "estado": "CREADO"}), 201


@bp.get("/ejemplos/<id_ejemplo>")
def obtener_ejemplo(id_ejemplo):
    resultado = ejecutar_query(ObtenerEjemplo(id_ejemplo=id_ejemplo)).resultado
    if resultado is None:
        raise APIError("Ejemplo no encontrado", 404)
    return jsonify(dataclasses.asdict(resultado)), 200
