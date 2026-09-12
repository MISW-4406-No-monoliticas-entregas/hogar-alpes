"""Mapeador entre el agregado Sincronizacion y su modelo SQLAlchemy."""
import uuid

from modulos.sincronizaciones.dominio.entidades import Sincronizacion
from modulos.sincronizaciones.dominio.objetos_valor import (
    PartnerId,
    IdExterno,
    EstadoSincronizacion,
)
from modulos.sincronizaciones.infraestructura.dto import SincronizacionDTO


def _a_ms(dt) -> int:
    return int(dt.timestamp() * 1000)


class MapeadorSincronizacionDTO:
    def entidad_a_dto(self, s: Sincronizacion) -> SincronizacionDTO:
        publicado = (
            _a_ms(s.fecha_actualizacion)
            if s.estado == EstadoSincronizacion.PUBLICADA else None
        )
        return SincronizacionDTO(
            id=str(s.id),
            partner_id=s.partner_id.valor,
            id_externo=s.id_externo.valor,
            id_siniestro=s.id_siniestro,
            estado=s.estado.value,
            recibido_en=_a_ms(s.fecha_creacion),
            publicado_en=publicado,
        )

    def dto_a_entidad(self, dto: SincronizacionDTO) -> Sincronizacion:
        return Sincronizacion(
            id=uuid.UUID(dto.id),
            partner_id=PartnerId(dto.partner_id),
            id_externo=IdExterno(dto.id_externo),
            estado=EstadoSincronizacion(dto.estado),
            id_siniestro=dto.id_siniestro,
        )
