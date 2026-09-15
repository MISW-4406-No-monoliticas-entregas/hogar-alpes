"""Modelos SQLAlchemy del módulo siniestros (escritura).

- `eventos_siniestro` es el EVENT STORE: la fuente de verdad del agregado.
- `siniestros` era la tabla CRUD de la E3; se conserva solo para no romper
  datos existentes, pero el repositorio activo ya no la escribe.
"""
from sqlalchemy import Column, String, Float, DateTime, JSON, Integer, UniqueConstraint

from config.db import Base


class EventoSiniestroDTO(Base):
    __tablename__ = "eventos_siniestro"
    # (siniestro_id, version) único => control de concurrencia optimista: dos
    # escritores que partieron de la misma versión chocan aquí y uno falla.
    __table_args__ = (
        UniqueConstraint("siniestro_id", "version", name="uq_eventos_siniestro_version"),
    )

    id = Column(String(36), primary_key=True)  # id del evento de dominio
    siniestro_id = Column(String(36), nullable=False, index=True)
    tipo = Column(String(100), nullable=False)
    version = Column(Integer, nullable=False)
    fecha = Column(DateTime, nullable=False)
    datos = Column(JSON, nullable=False)


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
