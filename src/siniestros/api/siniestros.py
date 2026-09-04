"""Blueprint de la API HTTP (adaptador de entrada).

La capa web es delgada: traduce HTTP a comandos/queries y despacha por los
mediadores. No contiene reglas de negocio ni toca la BD directamente (ítem 2).
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
