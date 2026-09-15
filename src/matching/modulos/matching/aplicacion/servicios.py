"""Fábricas de Unidad de Trabajo y repositorios del módulo matching."""
from seedwork.infraestructura.uow_sqlalchemy import UnidadDeTrabajoSQLAlchemy
from config.db import SessionLocal
from modulos.matching.infraestructura.repositorios import (
    RepositorioAsignacionesSQLAlchemy,
    RepositorioProveedoresHabilitadosSQLAlchemy,
)


def nueva_uow() -> UnidadDeTrabajoSQLAlchemy:
    return UnidadDeTrabajoSQLAlchemy(SessionLocal)


def repositorio_asignaciones_en(uow: UnidadDeTrabajoSQLAlchemy) -> RepositorioAsignacionesSQLAlchemy:
    return RepositorioAsignacionesSQLAlchemy(uow.session)


def repositorio_proveedores_en(
    uow: UnidadDeTrabajoSQLAlchemy,
) -> RepositorioProveedoresHabilitadosSQLAlchemy:
    return RepositorioProveedoresHabilitadosSQLAlchemy(uow.session)
