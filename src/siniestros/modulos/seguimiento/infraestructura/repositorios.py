"""Repositorio de lectura de la proyección estado_siniestro.

Encapsula el acceso a la tabla de lectura: upsert desde los handlers de eventos
y consultas para las queries. Cada operación abre y cierra su propia sesión
(las lecturas son independientes y así se pueden escalar réplicas de lectura).
"""
from datetime import datetime

from config.db import SessionLocal
from modulos.seguimiento.infraestructura.dto import EstadoSiniestroDTO


class RepositorioEstadoSiniestro:
    def registrar_o_actualizar(self, **campos):
        """Upsert de una fila de la proyección por id_siniestro."""
        session = SessionLocal()
        try:
            fila = session.get(EstadoSiniestroDTO, campos["id_siniestro"])
            if fila is None:
                fila = EstadoSiniestroDTO(id_siniestro=campos["id_siniestro"])
                session.add(fila)
            for clave, valor in campos.items():
                setattr(fila, clave, valor)
            fila.fecha_actualizacion = datetime.utcnow()
            session.commit()
        finally:
            session.close()

    def obtener_por_id(self, id_siniestro: str):
        session = SessionLocal()
        try:
            return session.get(EstadoSiniestroDTO, id_siniestro)
        finally:
            session.close()

    def listar_por_partner(self, partner_id: str):
        session = SessionLocal()
        try:
            return (
                session.query(EstadoSiniestroDTO)
                .filter_by(partner_id=partner_id)
                .all()
            )
        finally:
            session.close()
