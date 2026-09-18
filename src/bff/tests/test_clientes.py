"""Pruebas del cliente HTTP base: timeouts, errores de red y códigos de respuesta.

No levantan ningún servicio: la sesión de `requests` se reemplaza por un doble.
"""
from unittest.mock import MagicMock

import pytest
import requests

from clientes.base import ClienteHTTP
from clientes.cliente_orquestador import ClienteOrquestador
from clientes.cliente_s7 import ClienteS7
from clientes.cliente_s9 import ClienteS9
from clientes.errores import (
    RespuestaErronea,
    ServicioNoConfigurado,
    ServicioNoDisponible,
    TiempoAgotado,
)


def _respuesta_http(codigo: int, cuerpo=None, texto: str = ""):
    r = MagicMock(spec=requests.Response)
    r.status_code = codigo
    if cuerpo is not None:
        r.content = b"x"
        r.json.return_value = cuerpo
        r.text = str(cuerpo)
    elif texto:
        r.content = texto.encode()
        r.json.side_effect = ValueError("no es json")
        r.text = texto
    else:
        r.content = b""
    return r


def _cliente(clase=ClienteHTTP, url="http://servicio:5000"):
    sesion = MagicMock(spec=requests.Session)
    return clase(url, timeout_conexion=1.5, timeout_lectura=3.0, sesion=sesion), sesion


def test_get_devuelve_codigo_y_json_y_usa_timeouts():
    cliente, sesion = _cliente()
    sesion.request.return_value = _respuesta_http(200, {"estado": "ok"})

    respuesta = cliente.get("/salud", params={"a": "1"})

    assert respuesta.codigo == 200
    assert respuesta.cuerpo == {"estado": "ok"}
    sesion.request.assert_called_once_with(
        "GET", "http://servicio:5000/salud", timeout=(1.5, 3.0), params={"a": "1"}
    )


def test_post_envia_json():
    cliente, sesion = _cliente()
    sesion.request.return_value = _respuesta_http(202, {"id": "1"})

    respuesta = cliente.post("/ruta", {"campo": "valor"})

    assert respuesta.codigo == 202
    sesion.request.assert_called_once_with(
        "POST", "http://servicio:5000/ruta", timeout=(1.5, 3.0), json={"campo": "valor"}
    )


def test_url_base_sin_barra_final():
    cliente, sesion = _cliente(url="http://servicio:5000/")
    sesion.request.return_value = _respuesta_http(200, {})
    cliente.get("/x")
    assert sesion.request.call_args.args[1] == "http://servicio:5000/x"


def test_sin_url_configurada_no_intenta_conectar():
    cliente, sesion = _cliente(ClienteOrquestador, url="")
    with pytest.raises(ServicioNoConfigurado) as exc:
        cliente.obtener_saga("abc")
    assert exc.value.servicio == "S4 Orquestador"
    sesion.request.assert_not_called()


def test_conexion_rechazada_es_servicio_no_disponible():
    cliente, sesion = _cliente()
    sesion.request.side_effect = requests.exceptions.ConnectionError("rechazada")
    with pytest.raises(ServicioNoDisponible):
        cliente.get("/x")


def test_timeout_de_conexion_es_tiempo_agotado():
    cliente, sesion = _cliente()
    sesion.request.side_effect = requests.exceptions.ConnectTimeout()
    with pytest.raises(TiempoAgotado):
        cliente.get("/x")


def test_timeout_de_lectura_es_tiempo_agotado():
    cliente, sesion = _cliente()
    sesion.request.side_effect = requests.exceptions.ReadTimeout()
    with pytest.raises(TiempoAgotado):
        cliente.get("/x")


def test_respuesta_4xx_levanta_respuesta_erronea_con_codigo_y_cuerpo():
    cliente, sesion = _cliente()
    sesion.request.return_value = _respuesta_http(404, {"error": "no existe"})
    with pytest.raises(RespuestaErronea) as exc:
        cliente.get("/x")
    assert exc.value.codigo == 404
    assert exc.value.cuerpo == {"error": "no existe"}
    assert exc.value.mensaje == "no existe"


def test_respuesta_4xx_sin_campo_error_usa_mensaje_generico_por_codigo():
    cliente, sesion = _cliente(ClienteS9)
    sesion.request.return_value = _respuesta_http(409, {"estado": "DUPLICADA"})
    with pytest.raises(RespuestaErronea) as exc:
        cliente.registrar_siniestro("seguros-alpes", {"numeroReclamo": "SA-1"})
    assert exc.value.codigo == 409
    assert exc.value.mensaje == "S9 Integraciones: solicitud duplicada o en conflicto"


def test_respuesta_5xx_levanta_respuesta_erronea():
    cliente, sesion = _cliente()
    sesion.request.return_value = _respuesta_http(500, texto="<html>boom</html>")
    with pytest.raises(RespuestaErronea) as exc:
        cliente.get("/x")
    assert exc.value.codigo == 500
    assert exc.value.cuerpo == {"error": "<html>boom</html>"}


def test_cuerpo_vacio_devuelve_none():
    cliente, sesion = _cliente()
    sesion.request.return_value = _respuesta_http(204)
    assert cliente.get("/x").cuerpo is None


# --- rutas de los clientes concretos (deben coincidir con los servicios reales) ---

def test_cliente_s9_registra_en_la_ruta_del_partner():
    cliente, sesion = _cliente(ClienteS9)
    sesion.request.return_value = _respuesta_http(202, {"id_sincronizacion": "s-1"})
    cliente.registrar_siniestro("seguros-alpes", {"numeroReclamo": "SA-1"})
    assert sesion.request.call_args.args[1] == (
        "http://servicio:5000/partners/seguros-alpes/siniestros"
    )
    assert sesion.request.call_args.kwargs["json"] == {"numeroReclamo": "SA-1"}


def test_cliente_s7_lista_proveedores_por_zona_y_servicio():
    cliente, sesion = _cliente(ClienteS7)
    sesion.request.return_value = _respuesta_http(200, [])
    cliente.listar_proveedores("bogota-norte", "plomeria")
    assert sesion.request.call_args.args[1] == "http://servicio:5000/proveedores"
    assert sesion.request.call_args.kwargs["params"] == {
        "zona": "bogota-norte",
        "servicio": "plomeria",
    }


def test_cliente_orquestador_consulta_sagas():
    cliente, sesion = _cliente(ClienteOrquestador)
    sesion.request.return_value = _respuesta_http(200, {"estado": "COMPLETADA"})
    cliente.obtener_saga("sin-1")
    assert sesion.request.call_args.args[1] == "http://servicio:5000/sagas/sin-1"
