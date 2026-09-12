"""Vistas de lectura del módulo ejemplo (lado de consulta)."""
from config.db import SessionLocal
from modulos.ejemplo.aplicacion.dto import EjemploDTO as EjemploLecturaDTO
from modulos.ejemplo.infraestructura.dto import EjemploDTO


def obtener(id_ejemplo: str) -> EjemploLecturaDTO | None:
    session = SessionLocal()
    try:
        fila = session.get(EjemploDTO, id_ejemplo)
        if fila is None:
            return None
        return EjemploLecturaDTO(id=fila.id, nombre=fila.nombre, estado=fila.estado)
    finally:
        session.close()
