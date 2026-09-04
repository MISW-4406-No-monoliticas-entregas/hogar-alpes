"""Modelo SQLAlchemy del lado de escritura (tabla `siniestros`).

Es un DTO de persistencia, no una entidad de dominio: por eso vive en infra.
Las entidades hijas (evidencias, actividades) se guardan como JSON dentro de la
misma fila del agregado (dos tablas bastan, según la rúbrica).
"""
from sqlalchemy import Column, String, Float, DateTime, JSON

from config.db import Base


class SiniestroDTO(Base):
    __tablename__ = "siniestros"

    id = Column(String(36), primary_key=True)
    partner_id = Column(String(100), nullable=False, index=True)
    poliza = Column(String(100), nullable=False)
    monto = Column(Float, nullable=False)
    moneda = Column(String(3), nullable=False, default="COP")
    calle = Column(String(200))
    ciudad = Column(String(100))
    pais = Column(String(2), default="CO")
    estado = Column(String(20), nullable=False)
    proveedor_id = Column(String(100), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
    evidencias = Column(JSON, default=list)
    actividades = Column(JSON, default=list)
