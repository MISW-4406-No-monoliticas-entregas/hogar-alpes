"""Vistas de lectura del módulo matching (lado de consulta)."""
from config.db import SessionLocal
from modulos.matching.aplicacion.dto import ProveedorHabilitadoDTO as ProveedorLecturaDTO
from modulos.matching.infraestructura.dto import ProveedorHabilitadoDTO


def listar_por_zona_servicio(zona: str, servicio: str) -> list[ProveedorLecturaDTO]:
    session = SessionLocal()
    try:
        filas = (
            session.query(ProveedorHabilitadoDTO)
            .filter(
                ProveedorHabilitadoDTO.zona == zona,
                ProveedorHabilitadoDTO.servicio == servicio,
            )
            .order_by(ProveedorHabilitadoDTO.nombre)
            .all()
        )
        return [
            ProveedorLecturaDTO(
                id=fila.id,
                nombre=fila.nombre,
                servicio=fila.servicio,
                zona=fila.zona,
                disponible=fila.disponible,
            )
            for fila in filas
        ]
    finally:
        session.close()
