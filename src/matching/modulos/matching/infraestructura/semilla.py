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
    ("Plomería Los Alpes", "plomeria", "norte", True),
    ("Plomería Express Bogotá", "plomeria", "norte", False),
    ("Electricistas del Valle", "electricidad", "norte", True),
    ("Vidrios Andinos", "vidrieria", "norte", False),
    ("Cerrajería Central", "cerrajeria", "sur", True),
    ("Plomería del Sur", "plomeria", "sur", False),
    ("Electricistas Unidos", "electricidad", "occidente", False),
    ("Gasfitería Oriente", "gasfiteria", "oriente", True),
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
