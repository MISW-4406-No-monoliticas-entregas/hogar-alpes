"""Repositorio CRUD del Saga Log con SQLAlchemy (adaptador de salida)."""
import uuid

from modulos.orquestador.dominio.repositorios import RepositorioSagas
from modulos.orquestador.dominio.entidades import Saga
from modulos.orquestador.dominio.objetos_valor import PasoSaga
from modulos.orquestador.infraestructura.dto import SagaDTO
from modulos.orquestador.infraestructura.mapeadores import MapeadorSagaDTO


class RepositorioSagasSQLAlchemy(RepositorioSagas):
    def __init__(self, session):
        self.session = session
        self.mapeador = MapeadorSagaDTO()

    def obtener_por_id(self, id: uuid.UUID) -> Saga | None:
        dto = self.session.get(SagaDTO, str(id))
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def obtener_por_siniestro(self, siniestro_id: str) -> Saga | None:
        dto = (
            self.session.query(SagaDTO)
            .filter(SagaDTO.siniestro_id == siniestro_id)
            .order_by(SagaDTO.fecha_creacion.desc())
            .first()
        )
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def obtener_pendiente(self, partner_id: str, poliza: str) -> Saga | None:
        """La saga que espera id_siniestro para este partner y esta poliza.

        Se toma la mas antigua: si el mismo partner reenvia la misma poliza
        antes de que S2 responda, se atienden en el orden en que entraron.
        """
        dto = (
            self.session.query(SagaDTO)
            .filter(SagaDTO.partner_id == partner_id)
            .filter(SagaDTO.poliza == poliza)
            .filter(SagaDTO.paso_actual == PasoSaga.PENDIENTE.value)
            .order_by(SagaDTO.fecha_creacion.asc())
            .first()
        )
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def agregar(self, saga: Saga):
        self.session.add(self.mapeador.entidad_a_dto(saga))

    def actualizar(self, saga: Saga):
        self.session.merge(self.mapeador.entidad_a_dto(saga))
