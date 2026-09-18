"""Pruebas de las rutas del BFF con los clientes reemplazados por dobles.

Verifican (a) que cada ruta le pega al servicio correcto con los argumentos
correctos y (b) que los errores de los clientes se traducen a los códigos
documentados en api/errores.py.
"""
from unittest.mock import patch

import pytest

from api import create_app
from clientes.base import Respuesta
from clientes.errores import (
    RespuestaErronea,
    ServicioNoConfigurado,
    ServicioNoDisponible,
    TiempoAgotado,
)


@pytest.fixture
def cliente():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


# --- POST /siniestros -> S9 ---------------------------------------------------

def test_registrar_siniestro_reenvia_a_s9_el_payload_del_partner(cliente):
    payload = {"numeroReclamo": "SA-1", "poliza": "POL-1", "montoEstimado": 1}
    with patch("api.siniestros.s9.registrar_siniestro") as registrar:
        registrar.return_value = Respuesta(202, {"id_sincronizacion": "s-1", "estado": "PUBLICADA"})
        r = cliente.post("/siniestros", json={"partner_id": "seguros-alpes", "siniestro": payload})

    assert r.status_code == 202
    assert r.get_json() == {"id_sincronizacion": "s-1", "estado": "PUBLICADA"}
    registrar.assert_called_once_with("seguros-alpes", payload)


def test_registrar_siniestro_conserva_409_duplicado_de_s9(cliente):
    with patch("api.siniestros.s9.registrar_siniestro") as registrar:
        registrar.side_effect = RespuestaErronea("S9 Integraciones", 409, {"estado": "DUPLICADA"})
        r = cliente.post("/siniestros", json={"partner_id": "seguros-alpes", "siniestro": {"a": 1}})

    assert r.status_code == 409
    assert r.get_json()["servicio"] == "S9 Integraciones"
    assert r.get_json()["detalle"] == {"estado": "DUPLICADA"}


@pytest.mark.parametrize(
    "cuerpo",
    [
        None,
        {},
        {"siniestro": {"a": 1}},
        {"partner_id": "seguros-alpes"},
        {"partner_id": "seguros-alpes", "siniestro": {}},
        {"partner_id": "", "siniestro": {"a": 1}},
    ],
)
def test_registrar_siniestro_valida_el_cuerpo_sin_llamar_a_s9(cliente, cuerpo):
    with patch("api.siniestros.s9.registrar_siniestro") as registrar:
        r = cliente.post("/siniestros", json=cuerpo)
    assert r.status_code == 400
    assert "error" in r.get_json()
    registrar.assert_not_called()


# --- GET /siniestros/<id> -> S2 ----------------------------------------------

def test_obtener_siniestro_le_pega_a_s2(cliente):
    with patch("api.siniestros.s2.obtener_siniestro") as obtener:
        obtener.return_value = Respuesta(200, {"id_siniestro": "x", "estado": "REGISTRADO"})
        r = cliente.get("/siniestros/x")
    assert r.status_code == 200
    assert r.get_json()["estado"] == "REGISTRADO"
    obtener.assert_called_once_with("x")


def test_obtener_siniestro_404_de_s2_se_conserva(cliente):
    with patch("api.siniestros.s2.obtener_siniestro") as obtener:
        obtener.side_effect = RespuestaErronea(
            "S2 Siniestros", 404, {"error": "Siniestro no encontrado en la proyección"}
        )
        r = cliente.get("/siniestros/x")
    assert r.status_code == 404
    assert r.get_json()["error"] == "Siniestro no encontrado en la proyección"
    assert r.get_json()["servicio"] == "S2 Siniestros"


def test_listar_siniestros_por_partner_le_pega_a_s2(cliente):
    with patch("api.siniestros.s2.listar_siniestros_por_partner") as listar:
        listar.return_value = Respuesta(200, [])
        r = cliente.get("/partners/seguros-alpes/siniestros")
    assert r.status_code == 200
    listar.assert_called_once_with("seguros-alpes")


# --- GET /siniestros/<id>/estado -> orquestador --------------------------------

def test_estado_transaccion_le_pega_al_orquestador(cliente):
    saga = {"id_siniestro": "x", "paso_actual": "AsignarProveedor", "estado": "EN_PROGRESO", "historial": []}
    with patch("api.siniestros.orquestador.obtener_saga") as obtener:
        obtener.return_value = Respuesta(200, saga)
        r = cliente.get("/siniestros/x/estado")
    assert r.status_code == 200
    assert r.get_json() == saga
    obtener.assert_called_once_with("x")


def test_estado_transaccion_sin_orquestador_responde_501_claro(cliente):
    with patch("api.siniestros.orquestador.obtener_saga") as obtener:
        obtener.side_effect = ServicioNoConfigurado("S4 Orquestador", "URL no configurada")
        r = cliente.get("/siniestros/x/estado")
    assert r.status_code == 501
    assert "S4 Orquestador" in r.get_json()["error"]
    assert r.get_json()["servicio"] == "S4 Orquestador"


# --- GET /siniestros/<id>/asignacion -> S7 -----------------------------------

def test_asignacion_le_pega_a_s7(cliente):
    with patch("api.siniestros.s7.obtener_asignacion") as obtener:
        obtener.return_value = Respuesta(200, {"estado": "ASIGNADA"})
        r = cliente.get("/siniestros/x/asignacion")
    assert r.status_code == 200
    obtener.assert_called_once_with("x")


# --- GET /reglas/<partner_id> -> S10 ----------------------------------------

def test_reglas_le_pega_a_s10(cliente):
    with patch("api.reglas.s10.obtener_reglas") as obtener:
        obtener.return_value = Respuesta(200, {"partner_id": "seguros-alpes"})
        r = cliente.get("/reglas/seguros-alpes")
    assert r.status_code == 200
    obtener.assert_called_once_with("seguros-alpes")


def test_validaciones_le_pega_a_s10_con_limite(cliente):
    with patch("api.reglas.s10.listar_validaciones") as listar:
        listar.return_value = Respuesta(200, [])
        r = cliente.get("/reglas/seguros-alpes/validaciones?limite=5")
    assert r.status_code == 200
    listar.assert_called_once_with("seguros-alpes", 5)


def test_validaciones_sin_limite_no_lo_envia(cliente):
    with patch("api.reglas.s10.listar_validaciones") as listar:
        listar.return_value = Respuesta(200, [])
        cliente.get("/reglas/seguros-alpes/validaciones")
    listar.assert_called_once_with("seguros-alpes", None)


def test_validaciones_con_limite_invalido_es_400(cliente):
    with patch("api.reglas.s10.listar_validaciones") as listar:
        r = cliente.get("/reglas/seguros-alpes/validaciones?limite=abc")
    assert r.status_code == 400
    listar.assert_not_called()


# --- GET /proveedores -> S7 ---------------------------------------------------

def test_proveedores_le_pega_a_s7(cliente):
    with patch("api.proveedores.s7.listar_proveedores") as listar:
        listar.return_value = Respuesta(200, [{"nombre": "Plomería Los Alpes"}])
        r = cliente.get("/proveedores?zona=bogota-norte&servicio=plomeria")
    assert r.status_code == 200
    listar.assert_called_once_with("bogota-norte", "plomeria")


def test_proveedores_sin_parametros_es_400_sin_llamar_a_s7(cliente):
    with patch("api.proveedores.s7.listar_proveedores") as listar:
        r = cliente.get("/proveedores?zona=bogota-norte")
    assert r.status_code == 400
    listar.assert_not_called()


# --- traducción de errores de red ---------------------------------------------

def test_servicio_caido_responde_503(cliente):
    with patch("api.siniestros.s2.obtener_siniestro") as obtener:
        obtener.side_effect = ServicioNoDisponible("S2 Siniestros", "no se pudo conectar")
        r = cliente.get("/siniestros/x")
    assert r.status_code == 503
    assert r.get_json()["servicio"] == "S2 Siniestros"


def test_timeout_responde_504(cliente):
    with patch("api.siniestros.s2.obtener_siniestro") as obtener:
        obtener.side_effect = TiempoAgotado("S2 Siniestros", "no respondió a tiempo")
        r = cliente.get("/siniestros/x")
    assert r.status_code == 504


def test_error_interno_del_servicio_responde_502(cliente):
    with patch("api.siniestros.s2.obtener_siniestro") as obtener:
        obtener.side_effect = RespuestaErronea("S2 Siniestros", 500, {"error": "boom"})
        r = cliente.get("/siniestros/x")
    assert r.status_code == 502
    assert r.get_json()["detalle"] == {"error": "boom"}


# --- salud --------------------------------------------------------------------

def test_salud_del_bff(cliente):
    r = cliente.get("/salud")
    assert r.status_code == 200
    assert r.get_json() == {"estado": "ok", "servicio": "bff"}


def test_salud_dependencias_reporta_ok_caido_y_no_integrado(cliente):
    from clientes import todos

    def _get(self_cliente):
        def _f(ruta, params=None):
            if self_cliente.nombre == "S2 Siniestros":
                raise ServicioNoDisponible(self_cliente.nombre, "no se pudo conectar")
            if self_cliente.nombre == "S4 Orquestador":
                raise ServicioNoConfigurado(self_cliente.nombre, "URL no configurada")
            return Respuesta(200, {"estado": "ok"})
        return _f

    parches = [patch.object(c, "get", _get(c)) for c in todos]
    for p in parches:
        p.start()
    try:
        r = cliente.get("/salud/dependencias")
    finally:
        for p in parches:
            p.stop()

    assert r.status_code == 200
    reporte = r.get_json()
    assert reporte["S9 Integraciones"]["estado"] == "ok"
    assert reporte["S2 Siniestros"]["estado"] == "caido"
    assert reporte["S4 Orquestador"]["estado"] == "no_integrado"
