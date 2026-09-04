"""Fábrica de repositorios del módulo siniestros (infraestructura).

Permite obtener el adaptador concreto de repositorio a partir de una sesión, sin
que quien lo pide conozca la clase concreta.
"""
from modulos.siniestros.infraestructura.repositorios import (
    RepositorioSiniestrosSQLAlchemy,
)


class FabricaRepositorio:
    def crear_repositorio_siniestros(self, session) -> RepositorioSiniestrosSQLAlchemy:
        return RepositorioSiniestrosSQLAlchemy(session)
