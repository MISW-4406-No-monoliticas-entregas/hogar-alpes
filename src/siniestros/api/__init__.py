"""Fábrica de la aplicación Flask (composition root del adaptador HTTP)."""
import logging

from flask import Flask, jsonify


def _registrar_suscripciones_de_eventos():
    """Registra los handlers de eventos de dominio (señales) de ambos módulos.

    Debe ejecutarse una sola vez al arrancar el proceso, ANTES de atender
    comandos, para que las proyecciones y la publicación a Pulsar reaccionen.
    """
    from modulos.siniestros.aplicacion import handlers as h_siniestros
    from modulos.seguimiento.aplicacion import handlers as h_seguimiento

    h_siniestros.registrar_handlers()
    h_seguimiento.registrar_handlers()


def _importar_handlers_de_comandos_y_queries():
    """Importa los módulos que registran los handlers de singledispatch."""
    from modulos.siniestros.aplicacion.comandos import registrar_siniestro
    from modulos.siniestros.aplicacion.comandos import asignar_proveedor
    from modulos.seguimiento.aplicacion.queries import obtener_estado_siniestro
    from modulos.seguimiento.aplicacion.queries import listar_siniestros_por_partner


def create_app(iniciar_broker: bool = True) -> Flask:
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)

    from config.db import crear_tablas
    crear_tablas()

    if iniciar_broker:
        from seedwork.infraestructura.broker import configurar_namespace_multiesquema
        from config.settings import PULSAR_ADMIN_URL
        configurar_namespace_multiesquema(PULSAR_ADMIN_URL)

    _importar_handlers_de_comandos_y_queries()
    _registrar_suscripciones_de_eventos()

    from seedwork.presentacion.api import registrar_manejadores_error
    registrar_manejadores_error(app)

    from api.siniestros import bp
    app.register_blueprint(bp)

    @app.get("/salud")
    def salud():
        return jsonify({"estado": "ok"}), 200

    return app
