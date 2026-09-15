"""Fabrica de la aplicacion Flask (adaptador de entrada HTTP)."""
import logging

from flask import Flask, jsonify


def _registrar_suscripciones_de_eventos():
    from modulos.reglas.aplicacion import handlers as h_reglas
    h_reglas.registrar_handlers()


def _importar_handlers_de_comandos_y_queries():
    from modulos.reglas.aplicacion.comandos import validar_siniestro  # noqa: F401
    from modulos.reglas.aplicacion.queries import obtener_reglas_partner  # noqa: F401
    from modulos.reglas.aplicacion.queries import obtener_validaciones  # noqa: F401


def create_app() -> Flask:
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)

    from config.db import crear_tablas
    crear_tablas()

    _importar_handlers_de_comandos_y_queries()
    _registrar_suscripciones_de_eventos()

    from config.settings import CARGAR_SEMILLA
    if CARGAR_SEMILLA:
        from modulos.reglas.infraestructura.semilla import cargar_semilla
        cargar_semilla()

    from seedwork.presentacion.api import registrar_manejadores_error
    registrar_manejadores_error(app)

    from api.reglas import bp
    app.register_blueprint(bp)

    @app.get("/salud")
    def salud():
        return jsonify({"estado": "ok"}), 200

    return app
