"""Modelo SQLAlchemy de la tabla ejemplos (CRUD)."""
from sqlalchemy import Column, String, DateTime

from config.db import Base


class EjemploDTO(Base):
    __tablename__ = "ejemplos"

    id = Column(String(36), primary_key=True)
    nombre = Column(String(200), nullable=False)
    estado = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=False)
