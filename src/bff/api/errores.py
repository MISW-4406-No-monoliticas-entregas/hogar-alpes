"""Traducción de los errores de los clientes a respuestas HTTP del BFF.

Regla: el cliente del BFF siempre recibe JSON `{"error": ..., "servicio": ...}`
con un código que dice qué pasó, nunca un timeout silencioso ni un 500 opaco.

| Error del cliente        | Código BFF | Significado                                   |
|--------------------------|-----------:|-----------------------------------------------|
| ServicioNoConfigurado    |        501 | Ese servicio aún no está integrado (S4)       |
| ServicioNoDisponible     |        503 | No se pudo conectar (caído / no arrancó)      |
| TiempoAgotado            |        504 | Conectó pero no respondió dentro del timeout  |
| RespuestaErronea 4xx     | mismo 4xx  | Error del cliente, se conserva (400/404/409)  |
| RespuestaErronea 5xx     |        502 | El servicio falló internamente                |
"""
from flask import jsonify

from clientes.errores import (
    RespuestaErronea,
    ServicioNoConfigurado,
    ServicioNoDisponible,
    TiempoAgotado,
)


class APIError(Exception):
    """Error de validación propio del BFF (p. ej. cuerpo incompleto)."""

    def __init__(self, descripcion: str, code: int = 400):
        self.descripcion = descripcion
        self.code = code
        super().__init__(descripcion)


def _json_error(mensaje: str, codigo: int, servicio: str | None = None, detalle=None):
    cuerpo = {"error": mensaje}
    if servicio:
        cuerpo["servicio"] = servicio
    if detalle is not None:
        cuerpo["detalle"] = detalle
    return jsonify(cuerpo), codigo


def registrar_manejadores_error(app):
    @app.errorhandler(APIError)
    def _api(e: APIError):
        return _json_error(e.descripcion, e.code)

    @app.errorhandler(ServicioNoConfigurado)
    def _no_configurado(e: ServicioNoConfigurado):
        return _json_error(
            f"{e.servicio} todavía no está integrado en este despliegue ({e.mensaje})",
            501,
            e.servicio,
        )

    @app.errorhandler(ServicioNoDisponible)
    def _no_disponible(e: ServicioNoDisponible):
        return _json_error(f"{e.servicio} no está disponible: {e.mensaje}", 503, e.servicio)

    @app.errorhandler(TiempoAgotado)
    def _tiempo_agotado(e: TiempoAgotado):
        return _json_error(f"{e.servicio} {e.mensaje}", 504, e.servicio)

    @app.errorhandler(RespuestaErronea)
    def _respuesta_erronea(e: RespuestaErronea):
        if e.codigo >= 500:
            return _json_error(
                f"{e.servicio} respondió con un error interno ({e.codigo})",
                502,
                e.servicio,
                e.cuerpo,
            )
        # 4xx del servicio: es un error del cliente y se conserva el código.
        return _json_error(e.mensaje, e.codigo, e.servicio, e.cuerpo)
