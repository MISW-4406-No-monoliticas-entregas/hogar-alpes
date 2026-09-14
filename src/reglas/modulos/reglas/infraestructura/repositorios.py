"""Repositorios del modulo reglas con SQLAlchemy (adaptadores de salida)."""
import uuid

from modulos.reglas.dominio.entidades import ReglaDePartner, Validacion
from modulos.reglas.dominio.repositorios import (
    RepositorioReglasDePartner,
    RepositorioValidaciones,
)
from modulos.reglas.infraestructura.dto import ReglaDePartnerDTO, ValidacionDTO
from modulos.reglas.infraestructura.mapeadores import (
    MapeadorReglaDePartnerDTO,
    MapeadorValidacionDTO,
)


class RepositorioReglasDePartnerSQLAlchemy(RepositorioReglasDePartner):
    def __init__(self, session):
        self.session = session
        self.mapeador = MapeadorReglaDePartnerDTO()

    def obtener_por_id(self, id: uuid.UUID) -> ReglaDePartner | None:
        dto = self.session.get(ReglaDePartnerDTO, str(id))
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def obtener_por_partner(self, partner_id: str) -> ReglaDePartner | None:
        dto = (
            self.session.query(ReglaDePartnerDTO)
            .filter(ReglaDePartnerDTO.partner_id == partner_id)
            .one_or_none()
        )
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def agregar(self, regla: ReglaDePartner):
        self.session.add(self.mapeador.entidad_a_dto(regla))

    def actualizar(self, regla: ReglaDePartner):
        self.session.merge(self.mapeador.entidad_a_dto(regla))


class RepositorioValidacionesSQLAlchemy(RepositorioValidaciones):
    def __init__(self, session):
        self.session = session
        self.mapeador = MapeadorValidacionDTO()

    def obtener_por_id(self, id: uuid.UUID) -> Validacion | None:
        dto = self.session.get(ValidacionDTO, str(id))
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def listar_por_partner(self, partner_id: str, limite: int = 50) -> list[Validacion]:
        filas = (
            self.session.query(ValidacionDTO)
            .filter(ValidacionDTO.partner_id == partner_id)
            .order_by(ValidacionDTO.fecha_creacion.desc())
            .limit(limite)
            .all()
        )
        return [self.mapeador.dto_a_entidad(f) for f in filas]

    def agregar(self, validacion: Validacion):
        self.session.add(self.mapeador.entidad_a_dto(validacion))

    def actualizar(self, validacion: Validacion):
        self.session.merge(self.mapeador.entidad_a_dto(validacion))
