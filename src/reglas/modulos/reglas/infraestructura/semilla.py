"""Datos semilla: contratos de tres partners para demostrar aprobacion y rechazo."""
import logging

from modulos.reglas.dominio.fabricas import FabricaReglaDePartner
from modulos.reglas.dominio.objetos_valor import Monto, PartnerId, Servicio, Zona
from modulos.reglas.aplicacion.servicios import nueva_uow, repositorio_reglas_en

logger = logging.getLogger(__name__)

PARTNERS = [
    {
        "partner_id": "seguros-alpes",
        "monto_maximo": 8_000_000.0,
        "servicios": ["plomeria", "electricidad", "carpinteria"],
        "zonas": ["bogota-norte", "bogota-centro", "medellin"],
    },
    {
        "partner_id": "banco-andes",
        "monto_maximo": 2_500_000.0,
        "servicios": ["plomeria", "electricidad"],
        "zonas": ["bogota-norte"],
    },
    {
        "partner_id": "comercio-muebles",
        "monto_maximo": 1_200_000.0,
        "servicios": ["carpinteria"],
        "zonas": ["cali", "barranquilla"],
    },
]


def cargar_semilla() -> None:
    fabrica = FabricaReglaDePartner()
    with nueva_uow() as uow:
        repositorio = repositorio_reglas_en(uow)
        creados = 0
        for p in PARTNERS:
            if repositorio.obtener_por_partner(p["partner_id"]) is not None:
                continue
            regla = fabrica.crear_regla(
                partner_id=PartnerId(p["partner_id"]),
                monto_maximo=Monto(p["monto_maximo"], "COP"),
                servicios_cubiertos=[Servicio(s) for s in p["servicios"]],
                zonas_habilitadas=[Zona(z) for z in p["zonas"]],
            )
            repositorio.agregar(regla)
            creados += 1
        if creados:
            uow.commit()
        logger.info("Semilla de reglas: %s partners creados", creados)
