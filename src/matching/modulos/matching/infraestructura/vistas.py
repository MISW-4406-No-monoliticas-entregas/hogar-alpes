"""Vistas de lectura del módulo matching (lado de consulta)."""
from config.db import SessionLocal
from modulos.matching.aplicacion.dto import (
    ProveedorHabilitadoDTO as ProveedorLecturaDTO,
    AsignacionDTO as AsignacionLecturaDTO,
)
from modulos.matching.infraestructura.dto import ProveedorHabilitadoDTO, AsignacionDTO


def obtener_asignacion_por_siniestro(id_siniestro: str) -> AsignacionLecturaDTO | None:
    session = SessionLocal()
    try:
        fila = (
            session.query(AsignacionDTO)
            .filter(AsignacionDTO.id_siniestro == id_siniestro)
            .order_by(AsignacionDTO.fecha_creacion.desc())
            .first()
        )
        if fila is None:
            return None
        return AsignacionLecturaDTO(
            id=fila.id,
            id_siniestro=fila.id_siniestro,
            servicio=fila.servicio,
            zona=fila.zona,
            proveedor_id=fila.proveedor_id,
            nombre_proveedor=fila.nombre_proveedor,
            estado=fila.estado,
        )
    finally:
        session.close()


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
