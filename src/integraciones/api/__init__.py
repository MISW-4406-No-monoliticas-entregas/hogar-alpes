"""Fábrica de la aplicación Flask (adaptador de entrada HTTP)."""
import logging

from flask import Flask, jsonify


def _registrar_suscripciones_de_eventos():
    from modulos.sincronizaciones.aplicacion import handlers as h_sincro
    h_sincro.registrar_handlers()


def _importar_handlers_de_comandos_y_queries():
    from modulos.sincronizaciones.aplicacion.comandos import sincronizar_siniestro  # noqa: F401
    from modulos.sincronizaciones.aplicacion.queries import obtener_sincronizacion  # noqa: F401
    from modulos.sincronizaciones.aplicacion.queries import listar_sincronizaciones_por_partner  # noqa: F401


def create_app() -> Flask:
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)

    from config.db import crear_tablas
    crear_tablas()

    _importar_handlers_de_comandos_y_queries()
    _registrar_suscripciones_de_eventos()

    from seedwork.presentacion.api import registrar_manejadores_error
    registrar_manejadores_error(app)

    from api.sincronizaciones import bp
    app.register_blueprint(bp)

    @app.get("/salud")
    def salud():
        return jsonify({"estado": "ok"}), 200

    return app
