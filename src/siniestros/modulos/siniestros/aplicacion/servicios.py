"""Composición de la Unidad de Trabajo + repositorio para el módulo siniestros.

Aquí (capa de aplicación) es donde se ensamblan los adaptadores concretos con el
dominio: es el "composition root" del módulo. El DOMINIO nunca importa infra;
esta capa sí puede, porque su trabajo es orquestar el caso de uso.
"""
from seedwork.infraestructura.uow_sqlalchemy import UnidadDeTrabajoSQLAlchemy
from config.db import SessionLocal
from modulos.siniestros.infraestructura.repositorios import (
    RepositorioSiniestrosSQLAlchemy,
)


def nueva_uow() -> UnidadDeTrabajoSQLAlchemy:
    return UnidadDeTrabajoSQLAlchemy(SessionLocal)


def repositorio_en(uow: UnidadDeTrabajoSQLAlchemy) -> RepositorioSiniestrosSQLAlchemy:
    return RepositorioSiniestrosSQLAlchemy(uow.session)
