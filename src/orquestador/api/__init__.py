"""Fabrica de la aplicacion Flask (adaptador de entrada HTTP)."""
import logging

from flask import Flask, jsonify


def _registrar_suscripciones_de_eventos():
    from modulos.orquestador.aplicacion import handlers as h_orquestador
    h_orquestador.registrar_handlers()


def _importar_handlers_de_comandos_y_queries():
    from modulos.orquestador.aplicacion.comandos import pasos_felices  # noqa: F401
    from modulos.orquestador.aplicacion.comandos import compensaciones  # noqa: F401
    from modulos.orquestador.aplicacion.queries import obtener_saga  # noqa: F401


def create_app() -> Flask:
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)

    from config.db import crear_tablas
    crear_tablas()

    _importar_handlers_de_comandos_y_queries()
    _registrar_suscripciones_de_eventos()

    from seedwork.presentacion.api import registrar_manejadores_error
    registrar_manejadores_error(app)

    from api.sagas import bp
    app.register_blueprint(bp)

    @app.get("/salud")
    def salud():
        return jsonify({"estado": "ok"}), 200

    return app
