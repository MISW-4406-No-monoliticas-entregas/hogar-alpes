"""Cliente HTTP base: una sesión por servicio, timeouts y traducción de errores.

Cada cliente concreto (cliente_s9.py, cliente_s2.py, ...) hereda de aquí y solo
declara las rutas del servicio al que le habla. No hay lógica de negocio: se
envía la petición, se devuelve el JSON tal cual o se levanta un error tipado.
"""
import logging
from dataclasses import dataclass
from typing import Any

import requests

from clientes.errores import (
    RespuestaErronea,
    ServicioNoConfigurado,
    ServicioNoDisponible,
    TiempoAgotado,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Respuesta:
    codigo: int
    cuerpo: Any


class ClienteHTTP:
    nombre: str = "servicio"

    def __init__(
        self,
        url_base: str,
        timeout_conexion: float,
        timeout_lectura: float,
        sesion: requests.Session | None = None,
    ):
        self.url_base = (url_base or "").rstrip("/")
        self.timeout = (timeout_conexion, timeout_lectura)
        self.sesion = sesion or requests.Session()

    @property
    def configurado(self) -> bool:
        return bool(self.url_base)

    def get(self, ruta: str, params: dict | None = None) -> Respuesta:
        return self._solicitar("GET", ruta, params=params)

    def post(self, ruta: str, cuerpo: dict | None = None) -> Respuesta:
        return self._solicitar("POST", ruta, json=cuerpo)

    def _solicitar(self, metodo: str, ruta: str, **kwargs) -> Respuesta:
        if not self.configurado:
            raise ServicioNoConfigurado(
                self.nombre, "URL no configurada en este despliegue"
            )
        url = f"{self.url_base}{ruta}"
        try:
            respuesta = self.sesion.request(metodo, url, timeout=self.timeout, **kwargs)
        except requests.exceptions.ConnectTimeout as exc:
            raise TiempoAgotado(self.nombre, "no aceptó la conexión a tiempo") from exc
        except requests.exceptions.ReadTimeout as exc:
            raise TiempoAgotado(self.nombre, "no respondió a tiempo") from exc
        except requests.exceptions.ConnectionError as exc:
            raise ServicioNoDisponible(self.nombre, "no se pudo conectar") from exc
        except requests.exceptions.RequestException as exc:
            logger.exception("Error inesperado llamando a %s", url)
            raise ServicioNoDisponible(self.nombre, f"error de red: {exc}") from exc

        cuerpo = _cuerpo_json(respuesta)
        if respuesta.status_code >= 400:
            raise RespuestaErronea(self.nombre, respuesta.status_code, cuerpo)
        return Respuesta(codigo=respuesta.status_code, cuerpo=cuerpo)


def _cuerpo_json(respuesta: requests.Response):
    if not respuesta.content:
        return None
    try:
        return respuesta.json()
    except ValueError:
        return {"error": respuesta.text[:500]}
