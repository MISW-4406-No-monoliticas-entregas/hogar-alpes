"""Fabricas de Unidad de Trabajo y repositorios del modulo reglas."""
from seedwork.infraestructura.uow_sqlalchemy import UnidadDeTrabajoSQLAlchemy
from config.db import SessionLocal
from modulos.reglas.infraestructura.repositorios import (
    RepositorioReglasDePartnerSQLAlchemy,
    RepositorioValidacionesSQLAlchemy,
)


def nueva_uow() -> UnidadDeTrabajoSQLAlchemy:
    return UnidadDeTrabajoSQLAlchemy(SessionLocal)


def repositorio_reglas_en(uow: UnidadDeTrabajoSQLAlchemy) -> RepositorioReglasDePartnerSQLAlchemy:
    return RepositorioReglasDePartnerSQLAlchemy(uow.session)


def repositorio_validaciones_en(uow: UnidadDeTrabajoSQLAlchemy) -> RepositorioValidacionesSQLAlchemy:
    return RepositorioValidacionesSQLAlchemy(uow.session)
