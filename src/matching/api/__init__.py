"""Fábrica de la aplicación Flask (adaptador de entrada HTTP)."""
import logging

from flask import Flask, jsonify


def _registrar_suscripciones_de_eventos():
    """Conecta los handlers de eventos de dominio (mediador de señales)."""
    from modulos.matching.aplicacion import handlers as h_matching
    h_matching.registrar_handlers()


def _importar_handlers_de_comandos_y_queries():
    """Importa los módulos que registran los handlers en el singledispatch."""
    from modulos.matching.aplicacion.comandos import asignar_proveedor  # noqa: F401
    from modulos.matching.aplicacion.comandos import liberar_proveedor  # noqa: F401
    from modulos.matching.aplicacion.queries import listar_proveedores  # noqa: F401


def create_app() -> Flask:
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)

    from config.db import crear_tablas
    crear_tablas()

    _importar_handlers_de_comandos_y_queries()
    _registrar_suscripciones_de_eventos()

    from seedwork.presentacion.api import registrar_manejadores_error
    registrar_manejadores_error(app)

    from api.matching import bp
    app.register_blueprint(bp)

    @app.get("/salud")
    def salud():
        return jsonify({"estado": "ok"}), 200

    return app
