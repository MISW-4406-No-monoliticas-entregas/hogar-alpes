"""Fábrica de la aplicación Flask del BFF (adaptador HTTP de entrada)."""
import logging

from flask import Flask


def create_app() -> Flask:
    logging.basicConfig(level=logging.INFO)
    app = Flask(__name__)
    # Las respuestas de los servicios internos ya vienen con tildes y ñ.
    app.json.ensure_ascii = False

    from api.errores import registrar_manejadores_error
    registrar_manejadores_error(app)

    from api.salud import bp as bp_salud
    from api.siniestros import bp as bp_siniestros
    from api.reglas import bp as bp_reglas
    from api.proveedores import bp as bp_proveedores
    app.register_blueprint(bp_salud)
    app.register_blueprint(bp_siniestros)
    app.register_blueprint(bp_reglas)
    app.register_blueprint(bp_proveedores)

    return app
