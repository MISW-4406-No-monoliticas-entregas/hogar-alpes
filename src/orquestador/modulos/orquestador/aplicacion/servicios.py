"""Fábricas de Unidad de Trabajo y repositorio del módulo orquestador."""
from seedwork.infraestructura.uow_sqlalchemy import UnidadDeTrabajoSQLAlchemy
from config.db import SessionLocal
from modulos.orquestador.infraestructura.repositorios import RepositorioSagasSQLAlchemy


def nueva_uow() -> UnidadDeTrabajoSQLAlchemy:
    return UnidadDeTrabajoSQLAlchemy(SessionLocal)


def repositorio_sagas_en(uow: UnidadDeTrabajoSQLAlchemy) -> RepositorioSagasSQLAlchemy:
    return RepositorioSagasSQLAlchemy(uow.session)
