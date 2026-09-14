"""Fábricas de Unidad de Trabajo y repositorio del módulo sincronizaciones."""
from seedwork.infraestructura.uow_sqlalchemy import UnidadDeTrabajoSQLAlchemy
from config.db import SessionLocal
from modulos.sincronizaciones.infraestructura.repositorios import (
    RepositorioSincronizacionesSQLAlchemy,
)


def nueva_uow() -> UnidadDeTrabajoSQLAlchemy:
    return UnidadDeTrabajoSQLAlchemy(SessionLocal)


def repositorio_en(uow: UnidadDeTrabajoSQLAlchemy) -> RepositorioSincronizacionesSQLAlchemy:
    return RepositorioSincronizacionesSQLAlchemy(uow.session)
