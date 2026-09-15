"""Modelos SQLAlchemy (CRUD) del módulo matching: dos tablas propias.

`proveedores_habilitados` es una fila por (proveedor, servicio, zona): modelo
de lectura/config sembrado de antemano. `asignaciones` es el agregado
`Asignacion` (siniestro, proveedor asignado, estado, fechas).
"""
from sqlalchemy import Column, String, Boolean, DateTime

from config.db import Base


class ProveedorHabilitadoDTO(Base):
    __tablename__ = "proveedores_habilitados"

    id = Column(String(36), primary_key=True)
    nombre = Column(String(200), nullable=False)
    servicio = Column(String(100), nullable=False, index=True)
    zona = Column(String(100), nullable=False, index=True)
    disponible = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)


class AsignacionDTO(Base):
    __tablename__ = "asignaciones"

    id = Column(String(36), primary_key=True)
    id_siniestro = Column(String(36), nullable=False, index=True)
    servicio = Column(String(100), nullable=False)
    zona = Column(String(100), nullable=False)
    proveedor_id = Column(String(36), nullable=True)
    nombre_proveedor = Column(String(200), nullable=True)
    estado = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
