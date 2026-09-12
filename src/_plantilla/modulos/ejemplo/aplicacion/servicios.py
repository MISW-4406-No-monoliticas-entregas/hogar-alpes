"""Fábricas de Unidad de Trabajo y repositorio del módulo ejemplo."""
from seedwork.infraestructura.uow_sqlalchemy import UnidadDeTrabajoSQLAlchemy
from config.db import SessionLocal
from modulos.ejemplo.infraestructura.repositorios import RepositorioEjemplosSQLAlchemy


def nueva_uow() -> UnidadDeTrabajoSQLAlchemy:
    return UnidadDeTrabajoSQLAlchemy(SessionLocal)


def repositorio_en(uow: UnidadDeTrabajoSQLAlchemy) -> RepositorioEjemplosSQLAlchemy:
    return RepositorioEjemplosSQLAlchemy(uow.session)
