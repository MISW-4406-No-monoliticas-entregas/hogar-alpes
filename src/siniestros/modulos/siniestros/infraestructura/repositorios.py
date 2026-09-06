"""Repositorio de siniestros con SQLAlchemy."""
import uuid

from modulos.siniestros.dominio.repositorios import RepositorioSiniestros
from modulos.siniestros.dominio.entidades import Siniestro
from modulos.siniestros.infraestructura.dto import SiniestroDTO
from modulos.siniestros.infraestructura.mapeadores import MapeadorSiniestroDTO


class RepositorioSiniestrosSQLAlchemy(RepositorioSiniestros):
    def __init__(self, session):
        self.session = session
        self.mapeador = MapeadorSiniestroDTO()

    def obtener_por_id(self, id: uuid.UUID) -> Siniestro | None:
        dto = self.session.get(SiniestroDTO, str(id))
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def agregar(self, siniestro: Siniestro):
        self.session.add(self.mapeador.entidad_a_dto(siniestro))

    def actualizar(self, siniestro: Siniestro):
        nuevo = self.mapeador.entidad_a_dto(siniestro)
        self.session.merge(nuevo)
