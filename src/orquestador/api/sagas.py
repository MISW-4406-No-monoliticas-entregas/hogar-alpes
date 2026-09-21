"""Blueprint HTTP del orquestador de sagas (S4).

El POST arranca la transaccion larga. Es lo unico sincrono del servicio: a
partir de ahi todo avanza por comandos y eventos en Pulsar, y el cliente
consulta el progreso con los GET.

El GET /sagas/<id_siniestro> es el contrato que el BFF ya espera para
/siniestros/<id>/estado.
"""
import dataclasses

from flask import Blueprint, jsonify, request

from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.queries import ejecutar_query
from seedwork.presentacion.api import APIError
from modulos.orquestador.aplicacion.comandos.pasos_felices import IniciarSaga
from modulos.orquestador.aplicacion.queries.obtener_saga import (
    ObtenerSagaPorSiniestro,
    ObtenerSagaPorId,
    ListarSagas,
)

bp = Blueprint("sagas", __name__)

OBLIGATORIOS = ("partner_id", "poliza", "monto", "servicio", "zona")


@bp.post("/sagas")
def iniciar_saga():
    cuerpo = request.get_json(force=True, silent=True) or {}
    faltantes = [c for c in OBLIGATORIOS if not cuerpo.get(c)]
    if faltantes:
        raise APIError(f"Faltan campos: {', '.join(faltantes)}", 400)

    direccion = cuerpo.get("direccion") or {}
    id_saga = ejecutar_comando(
        IniciarSaga(
            partner_id=cuerpo["partner_id"],
            poliza=cuerpo["poliza"],
            monto=float(cuerpo["monto"]),
            moneda=cuerpo.get("moneda", "COP"),
            servicio=cuerpo["servicio"],
            zona=cuerpo["zona"],
            calle=direccion.get("calle", ""),
            ciudad=direccion.get("ciudad", ""),
            pais=direccion.get("pais", "CO"),
        )
    )
    return jsonify({"id_saga": id_saga, "paso_actual": "PENDIENTE"}), 202


@bp.get("/sagas/<id_siniestro>")
def obtener_saga_por_siniestro(id_siniestro):
    resultado = ejecutar_query(
        ObtenerSagaPorSiniestro(siniestro_id=id_siniestro)
    ).resultado
    if resultado is None:
        raise APIError("No hay saga para ese siniestro", 404)
    return jsonify(dataclasses.asdict(resultado)), 200


@bp.get("/sagas/por-id/<id_saga>")
def obtener_saga_por_id(id_saga):
    resultado = ejecutar_query(ObtenerSagaPorId(id_saga=id_saga)).resultado
    if resultado is None:
        raise APIError("No existe esa saga", 404)
    return jsonify(dataclasses.asdict(resultado)), 200


@bp.get("/sagas")
def listar_sagas():
    limite = int(request.args.get("limite", 50))
    resultado = ejecutar_query(ListarSagas(limite=limite)).resultado
    return jsonify([dataclasses.asdict(s) for s in resultado]), 200
