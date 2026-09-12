"""Repositorio de ejemplos con SQLAlchemy (adaptador de salida)."""
import uuid

from modulos.ejemplo.dominio.repositorios import RepositorioEjemplos
from modulos.ejemplo.dominio.entidades import Ejemplo
from modulos.ejemplo.infraestructura.dto import EjemploDTO
from modulos.ejemplo.infraestructura.mapeadores import MapeadorEjemploDTO


class RepositorioEjemplosSQLAlchemy(RepositorioEjemplos):
    def __init__(self, session):
        self.session = session
        self.mapeador = MapeadorEjemploDTO()

    def obtener_por_id(self, id: uuid.UUID) -> Ejemplo | None:
        dto = self.session.get(EjemploDTO, str(id))
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def agregar(self, ejemplo: Ejemplo):
        self.session.add(self.mapeador.entidad_a_dto(ejemplo))

    def actualizar(self, ejemplo: Ejemplo):
        self.session.merge(self.mapeador.entidad_a_dto(ejemplo))
