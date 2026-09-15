"""Repositorio de sincronizaciones con SQLAlchemy (adaptador de salida)."""
import uuid

from modulos.sincronizaciones.dominio.repositorios import RepositorioSincronizaciones
from modulos.sincronizaciones.dominio.entidades import Sincronizacion
from modulos.sincronizaciones.infraestructura.dto import SincronizacionDTO
from modulos.sincronizaciones.infraestructura.mapeadores import (
    MapeadorSincronizacionDTO,
)


class RepositorioSincronizacionesSQLAlchemy(RepositorioSincronizaciones):
    def __init__(self, session):
        self.session = session
        self.mapeador = MapeadorSincronizacionDTO()

    def obtener_por_id(self, id: uuid.UUID) -> Sincronizacion | None:
        dto = self.session.get(SincronizacionDTO, str(id))
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def existe(self, partner_id: str, id_externo: str) -> bool:
        return (
            self.session.query(SincronizacionDTO.id)
            .filter_by(partner_id=partner_id, id_externo=id_externo)
            .first()
            is not None
        )

    def agregar(self, sincronizacion: Sincronizacion):
        self.session.add(self.mapeador.entidad_a_dto(sincronizacion))

    def actualizar(self, sincronizacion: Sincronizacion):
        self.session.merge(self.mapeador.entidad_a_dto(sincronizacion))
