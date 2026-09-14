import pytest

from seedwork.dominio.excepciones import ReglaNegocioExcepcion
from modulos.reglas.dominio.fabricas import FabricaReglaDePartner, FabricaValidacion
from modulos.reglas.dominio.objetos_valor import (
    Monto,
    PartnerId,
    ResultadoValidacion,
    Servicio,
    Zona,
)
from modulos.reglas.dominio.eventos import (
    SiniestroAprobadoPorReglas,
    SiniestroRechazadoPorReglas,
)


def _regla():
    return FabricaReglaDePartner().crear_regla(
        partner_id=PartnerId("seguros-alpes"),
        monto_maximo=Monto(8_000_000.0, "COP"),
        servicios_cubiertos=[Servicio("plomeria"), Servicio("electricidad")],
        zonas_habilitadas=[Zona("bogota-norte")],
    )


def test_regla_sin_monto_maximo_positivo_no_se_crea():
    with pytest.raises(ReglaNegocioExcepcion):
        FabricaReglaDePartner().crear_regla(
            partner_id=PartnerId("seguros-alpes"),
            monto_maximo=Monto(0.0, "COP"),
            servicios_cubiertos=[Servicio("plomeria")],
            zonas_habilitadas=[Zona("bogota-norte")],
        )


def test_regla_sin_servicios_no_se_crea():
    with pytest.raises(ReglaNegocioExcepcion):
        FabricaReglaDePartner().crear_regla(
            partner_id=PartnerId("seguros-alpes"),
            monto_maximo=Monto(100.0, "COP"),
            servicios_cubiertos=[],
            zonas_habilitadas=[Zona("bogota-norte")],
        )


def test_siniestro_dentro_de_lo_pactado_se_aprueba():
    validacion = FabricaValidacion().crear_validacion(
        _regla(), "sin-1", Monto(500_000.0, "COP"), Servicio("plomeria"), Zona("bogota-norte")
    )
    assert validacion.resultado == ResultadoValidacion.APROBADO
    assert isinstance(validacion.eventos[0], SiniestroAprobadoPorReglas)


def test_monto_por_encima_del_maximo_se_rechaza():
    validacion = FabricaValidacion().crear_validacion(
        _regla(), "sin-2", Monto(9_000_000.0, "COP"), Servicio("plomeria"), Zona("bogota-norte")
    )
    assert validacion.resultado == ResultadoValidacion.RECHAZADO
    assert isinstance(validacion.eventos[0], SiniestroRechazadoPorReglas)
    assert "supera el maximo" in validacion.motivo


def test_servicio_no_cubierto_se_rechaza():
    validacion = FabricaValidacion().crear_validacion(
        _regla(), "sin-3", Monto(100_000.0, "COP"), Servicio("pintura"), Zona("bogota-norte")
    )
    assert validacion.resultado == ResultadoValidacion.RECHAZADO
    assert "no esta cubierto" in validacion.motivo


def test_zona_no_habilitada_se_rechaza():
    validacion = FabricaValidacion().crear_validacion(
        _regla(), "sin-4", Monto(100_000.0, "COP"), Servicio("plomeria"), Zona("cali")
    )
    assert validacion.resultado == ResultadoValidacion.RECHAZADO
    assert "no esta habilitada" in validacion.motivo


def test_partner_sin_reglas_se_rechaza():
    validacion = FabricaValidacion().crear_validacion_sin_regla(
        PartnerId("desconocido"), "sin-5", Monto(100.0, "COP"), Servicio("plomeria"), Zona("cali")
    )
    assert validacion.resultado == ResultadoValidacion.RECHAZADO
    assert "No hay reglas configuradas" in validacion.motivo
