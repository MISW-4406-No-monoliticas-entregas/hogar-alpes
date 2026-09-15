"""Modelos SQLAlchemy del modulo reglas (dos tablas, modelo CRUD)."""
from sqlalchemy import Boolean, Column, DateTime, Float, String

from config.db import Base


class ReglaDePartnerDTO(Base):
    __tablename__ = "reglas_partner"

    id = Column(String(36), primary_key=True)
    partner_id = Column(String(100), nullable=False, unique=True, index=True)
    monto_maximo = Column(Float, nullable=False)
    moneda = Column(String(3), nullable=False)
    servicios_cubiertos = Column(String(500), nullable=False)
    zonas_habilitadas = Column(String(500), nullable=False)
    activa = Column(Boolean, nullable=False, default=True)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)


class ValidacionDTO(Base):
    __tablename__ = "validaciones"

    id = Column(String(36), primary_key=True)
    id_siniestro = Column(String(100), nullable=False, index=True)
    partner_id = Column(String(100), nullable=False, index=True)
    monto = Column(Float, nullable=False)
    moneda = Column(String(3), nullable=False)
    servicio = Column(String(100), nullable=False)
    zona = Column(String(100), nullable=False)
    resultado = Column(String(20), nullable=False)
    motivo = Column(String(300), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
