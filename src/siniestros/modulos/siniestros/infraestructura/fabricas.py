"""Fábrica de repositorios del módulo siniestros."""
from modulos.siniestros.infraestructura.repositorios import (
    RepositorioSiniestrosSQLAlchemy,
)


class FabricaRepositorio:
    def crear_repositorio_siniestros(self, session) -> RepositorioSiniestrosSQLAlchemy:
        return RepositorioSiniestrosSQLAlchemy(session)
