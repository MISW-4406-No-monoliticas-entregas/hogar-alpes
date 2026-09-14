"""Manejo de errores de la API."""
from flask import jsonify

from seedwork.dominio.excepciones import ExcepcionDominio, ReglaNegocioExcepcion


class APIError(Exception):
    code = 500
    descripcion = "Error interno"

    def __init__(self, descripcion: str | None = None, code: int | None = None):
        if descripcion is not None:
            self.descripcion = descripcion
        if code is not None:
            self.code = code
        super().__init__(self.descripcion)


def registrar_manejadores_error(app):
    @app.errorhandler(ReglaNegocioExcepcion)
    def _regla_negocio(e: ReglaNegocioExcepcion):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(ExcepcionDominio)
    def _dominio(e: ExcepcionDominio):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(APIError)
    def _api(e: APIError):
        return jsonify({"error": e.descripcion}), e.code
