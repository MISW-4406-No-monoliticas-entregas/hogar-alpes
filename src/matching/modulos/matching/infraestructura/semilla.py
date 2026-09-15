"""Datos semilla de `proveedores_habilitados`.

Varios proveedores en distintas zonas y servicios, algunos disponibles y otros
no, para poder demostrar tanto la asignación exitosa (hay cobertura) como
SinProveedorDisponible (zona/servicio sin proveedor libre).
"""
import logging
from datetime import datetime

from seedwork.infraestructura.utils import generar_uuid
from modulos.matching.infraestructura.dto import ProveedorHabilitadoDTO

logger = logging.getLogger(__name__)

_PROVEEDORES = [
    # (nombre, servicio, zona, disponible)
    # Zonas y servicios alineados con el catálogo de S10 (seguros-alpes cubre
    # plomeria/electricidad/carpinteria en bogota-norte/bogota-centro/medellin)
    # para poder demostrar el flujo completo aprobado-por-reglas +
    # asignado-por-matching con los mismos valores de servicio/zona.
    ("Plomería Los Alpes", "plomeria", "bogota-norte", True),
    ("Plomería Express Bogotá", "plomeria", "bogota-norte", False),
    ("Electricistas del Valle", "electricidad", "bogota-norte", True),
    ("Carpintería Andina", "carpinteria", "bogota-norte", False),
    ("Cerrajería Central", "plomeria", "bogota-centro", True),
    ("Plomería del Sur", "plomeria", "medellin", False),
    ("Electricistas Unidos", "electricidad", "cali", False),
    ("Carpintería Pacífico", "carpinteria", "barranquilla", True),
]


def sembrar_proveedores(session) -> None:
    """Inserta el catálogo semilla si la tabla está vacía (idempotente)."""
    if session.query(ProveedorHabilitadoDTO).first() is not None:
        return

    ahora = datetime.utcnow()
    for nombre, servicio, zona, disponible in _PROVEEDORES:
        session.add(
            ProveedorHabilitadoDTO(
                id=generar_uuid(),
                nombre=nombre,
                servicio=servicio,
                zona=zona,
                disponible=disponible,
                fecha_creacion=ahora,
                fecha_actualizacion=ahora,
            )
        )
    session.commit()
    logger.info("Semilla de proveedores_habilitados insertada (%d filas)", len(_PROVEEDORES))
