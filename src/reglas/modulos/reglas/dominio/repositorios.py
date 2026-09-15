"""Puertos de salida del modulo reglas (interfaces en el dominio)."""
import uuid
from abc import abstractmethod

from seedwork.dominio.repositorios import Repositorio
from modulos.reglas.dominio.entidades import ReglaDePartner, Validacion


class RepositorioReglasDePartner(Repositorio):
    @abstractmethod
    def obtener_por_partner(self, partner_id: str) -> ReglaDePartner | None:
        ...


class RepositorioValidaciones(Repositorio):
    @abstractmethod
    def listar_por_partner(self, partner_id: str, limite: int = 50) -> list[Validacion]:
        ...
