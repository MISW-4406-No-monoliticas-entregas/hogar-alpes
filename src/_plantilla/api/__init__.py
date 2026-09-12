"""Fábrica de la aplicación Flask (adaptador de entrada HTTP)."""
import logging

from flask import Flask, jsonify


def _registrar_suscripciones_de_eventos():
    """Conecta los handlers de eventos de dominio (mediador de señales)."""
    from modulos.ejemplo.aplicacion import handlers as h_ejemplo
    h_ejemplo.registrar_handlers()


def _importar_handlers_de_comandos_y_queries():
    """Importa los módulos que registran los handlers en el singledispatch."""
    from modulos.ejemplo.aplicacion.comandos import crear_ejemplo  # noqa: F401
    from modulos.ejemplo.aplicacion.queries import obtener_ejemplo  # noqa: F401


def create_app() -> Flask:
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)

    from config.db import crear_tablas
    crear_tablas()

    _importar_handlers_de_comandos_y_queries()
    _registrar_suscripciones_de_eventos()

    from seedwork.presentacion.api import registrar_manejadores_error
    registrar_manejadores_error(app)

    from api.ejemplo import bp
    app.register_blueprint(bp)

    @app.get("/salud")
    def salud():
        return jsonify({"estado": "ok"}), 200

    return app
