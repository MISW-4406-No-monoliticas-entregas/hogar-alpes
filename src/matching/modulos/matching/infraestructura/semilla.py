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

# Pool de proveedores disponibles para los combos de demo. Matching marca al
# proveedor como no disponible al asignarlo (un trabajo por proveedor), así que
# un solo proveedor por combo se agota tras la primera saga feliz. Este pool da
# holgura para correr la colección/demo muchas veces mostrando COMPLETADA, sin
# perder el comportamiento de agotamiento bajo carga (escenario E3).
for _i in range(1, 21):
    _PROVEEDORES.append((f"Plomería Demo {_i:02d}", "plomeria", "bogota-norte", True))
    _PROVEEDORES.append((f"Electricistas Demo {_i:02d}", "electricidad", "bogota-norte", True))


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
