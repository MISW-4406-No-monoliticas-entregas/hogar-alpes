"""Blueprint de la API HTTP.

La ENTRADA DE PRODUCCIÓN de los comandos es el tópico comandos.siniestros
(ver modulos/siniestros/infraestructura/consumidores.py). Los POST de comandos
de este blueprint quedan como UTILIDADES DE PRUEBA: permiten ejercitar el flujo
sin publicar en Pulsar (demos y Postman). Las consultas (GET) sí son la
interfaz real de lectura y leen SOLO de la proyección estado_siniestro, nunca
del event store.
"""
import dataclasses

from flask import Blueprint, request, jsonify

from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.queries import ejecutar_query
from seedwork.presentacion.api import APIError
from modulos.siniestros.aplicacion.comandos.registrar_siniestro import (
    RegistrarSiniestro,
)
from modulos.siniestros.aplicacion.comandos.asignar_proveedor import (
    AsignarProveedor,
)
from modulos.siniestros.aplicacion.comandos.marcar_validado import MarcarValidado
from modulos.siniestros.aplicacion.comandos.rechazar_siniestro import (
    RechazarSiniestro,
)
from modulos.seguimiento.aplicacion.comandos.reconstruir_proyeccion import (
    ReconstruirProyeccion,
)
from modulos.seguimiento.aplicacion.queries.obtener_estado_siniestro import (
    ObtenerEstadoSiniestro,
)
from modulos.seguimiento.aplicacion.queries.listar_siniestros_por_partner import (
    ListarSiniestrosPorPartner,
)

bp = Blueprint("siniestros", __name__)


def _requerir(cuerpo: dict, *campos):
    faltantes = [c for c in campos if cuerpo.get(c) in (None, "")]
    if faltantes:
        raise APIError(f"Faltan campos: {', '.join(faltantes)}", 400)


# --------------------------------------------------------------------------
# Comandos por HTTP — utilidades de prueba (la entrada real es el tópico).
# --------------------------------------------------------------------------

@bp.post("/siniestros")
def registrar_siniestro():
    cuerpo = request.get_json(force=True, silent=True) or {}
    _requerir(cuerpo, "partner_id", "poliza", "monto", "calle", "ciudad")
    comando = RegistrarSiniestro(
        partner_id=cuerpo["partner_id"],
        poliza=cuerpo["poliza"],
        monto=float(cuerpo["monto"]),
        moneda=cuerpo.get("moneda", "COP"),
        calle=cuerpo["calle"],
        ciudad=cuerpo["ciudad"],
        pais=cuerpo.get("pais", "CO"),
    )
    id_siniestro = ejecutar_comando(comando)
    return jsonify({"id": id_siniestro, "estado": "REGISTRADO"}), 201


@bp.post("/siniestros/<id_siniestro>/proveedor")
def asignar_proveedor(id_siniestro):
    cuerpo = request.get_json(force=True, silent=True) or {}
    _requerir(cuerpo, "proveedor_id")
    ejecutar_comando(
        AsignarProveedor(id_siniestro=id_siniestro, proveedor_id=cuerpo["proveedor_id"])
    )
    return jsonify({"id": id_siniestro, "estado": "ASIGNADO"}), 200


@bp.post("/siniestros/<id_siniestro>/validar")
def marcar_validado(id_siniestro):
    ejecutar_comando(MarcarValidado(id_siniestro=id_siniestro))
    return jsonify({"id": id_siniestro, "estado": "VALIDADO"}), 200


@bp.post("/siniestros/<id_siniestro>/rechazar")
def rechazar_siniestro(id_siniestro):
    cuerpo = request.get_json(force=True, silent=True) or {}
    ejecutar_comando(
        RechazarSiniestro(
            id_siniestro=id_siniestro,
            motivo=cuerpo.get("motivo", "no_especificado"),
        )
    )
    return jsonify({"id": id_siniestro, "estado": "RECHAZADO"}), 200


# --------------------------------------------------------------------------
# Utilidad admin: reconstruir la proyección desde el event store.
# --------------------------------------------------------------------------

@bp.post("/admin/proyecciones/estado-siniestro/reconstruir")
def reconstruir_proyeccion():
    cuerpo = request.get_json(force=True, silent=True) or {}
    resultado = ejecutar_comando(
        ReconstruirProyeccion(id_siniestro=cuerpo.get("id_siniestro"))
    )
    return jsonify(resultado), 200


# --------------------------------------------------------------------------
# Consultas: leen SOLO de la proyección.
# --------------------------------------------------------------------------

@bp.get("/siniestros/<id_siniestro>")
def obtener_siniestro(id_siniestro):
    resultado = ejecutar_query(ObtenerEstadoSiniestro(id_siniestro=id_siniestro)).resultado
    if resultado is None:
        raise APIError("Siniestro no encontrado en la proyección", 404)
    return jsonify(dataclasses.asdict(resultado)), 200


@bp.get("/partners/<partner_id>/siniestros")
def listar_por_partner(partner_id):
    resultado = ejecutar_query(
        ListarSiniestrosPorPartner(partner_id=partner_id)
    ).resultado
    return jsonify([dataclasses.asdict(r) for r in resultado]), 200
