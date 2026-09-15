"""Fábricas de Unidad de Trabajo y repositorio del módulo siniestros."""
from seedwork.infraestructura.uow_sqlalchemy import UnidadDeTrabajoSQLAlchemy
from config.db import SessionLocal
from modulos.siniestros.infraestructura.repositorios import (
    RepositorioSiniestrosEventStore,
)


def nueva_uow() -> UnidadDeTrabajoSQLAlchemy:
    return UnidadDeTrabajoSQLAlchemy(SessionLocal)


def repositorio_en(uow: UnidadDeTrabajoSQLAlchemy) -> RepositorioSiniestrosEventStore:
    # Persistencia por event sourcing: mismo puerto del dominio, otro adaptador.
    return RepositorioSiniestrosEventStore(uow.session)
