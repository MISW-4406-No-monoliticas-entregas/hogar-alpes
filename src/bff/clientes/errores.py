"""Errores que levantan los clientes HTTP hacia los servicios internos.

La API los traduce a códigos HTTP claros para el cliente del BFF (ver
api/errores.py). Ningún error de un servicio interno se propaga "crudo".
"""


class ErrorCliente(Exception):
    """Base de los errores de los clientes. `servicio` es el nombre legible."""

    def __init__(self, servicio: str, mensaje: str):
        self.servicio = servicio
        self.mensaje = mensaje
        super().__init__(f"[{servicio}] {mensaje}")


class ServicioNoConfigurado(ErrorCliente):
    """La URL del servicio no está definida (p. ej. el orquestador aún no existe)."""


class ServicioNoDisponible(ErrorCliente):
    """No se pudo abrir conexión con el servicio (caído, DNS, conexión rechazada)."""


class TiempoAgotado(ErrorCliente):
    """El servicio aceptó la conexión pero no respondió a tiempo."""


_MENSAJES_POR_CODIGO = {
    400: "solicitud inválida",
    404: "recurso no encontrado",
    409: "solicitud duplicada o en conflicto",
}


class RespuestaErronea(ErrorCliente):
    """El servicio respondió con un código >= 400. Conserva código y cuerpo.

    El mensaje es el `error` que devolvió el servicio; si no trae uno (p. ej.
    el 409 de S9 solo trae `{"estado": "DUPLICADA"}`), se usa uno genérico por
    código para que el cliente del BFF nunca reciba solo un número.
    """

    def __init__(self, servicio: str, codigo: int, cuerpo):
        self.codigo = codigo
        self.cuerpo = cuerpo
        detalle = cuerpo.get("error") if isinstance(cuerpo, dict) else None
        generico = _MENSAJES_POR_CODIGO.get(codigo, f"respondió {codigo}")
        super().__init__(servicio, detalle or f"{servicio}: {generico}")
