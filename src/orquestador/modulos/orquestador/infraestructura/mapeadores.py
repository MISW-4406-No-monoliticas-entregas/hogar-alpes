"""Mapeador entre el agregado Saga y su modelo SQLAlchemy."""
import uuid

from modulos.orquestador.dominio.entidades import Saga
from modulos.orquestador.dominio.objetos_valor import PasoSaga, EstadoSaga
from modulos.orquestador.infraestructura.dto import SagaDTO


class MapeadorSagaDTO:
    def entidad_a_dto(self, s: Saga) -> SagaDTO:
        return SagaDTO(
            id=str(s.id),
            siniestro_id=s.siniestro_id,
            paso_actual=s.paso_actual.value,
            estado=s.estado.value,
            proveedor_id=s.proveedor_id,
            motivo_fallo=s.motivo_fallo,
            partner_id=s.partner_id,
            poliza=s.poliza,
            servicio=s.servicio,
            zona=s.zona,
            fecha_creacion=s.fecha_creacion,
            fecha_actualizacion=s.fecha_actualizacion,
        )

    def dto_a_entidad(self, dto: SagaDTO) -> Saga:
        saga = Saga(
            id=uuid.UUID(dto.id),
            siniestro_id=dto.siniestro_id,
            paso_actual=PasoSaga(dto.paso_actual),
            estado=EstadoSaga(dto.estado),
            proveedor_id=dto.proveedor_id,
            motivo_fallo=dto.motivo_fallo,
            partner_id=dto.partner_id,
            poliza=dto.poliza,
            servicio=dto.servicio,
            zona=dto.zona,
        )
        saga._fecha_creacion = dto.fecha_creacion
        saga._fecha_actualizacion = dto.fecha_actualizacion
        return saga
