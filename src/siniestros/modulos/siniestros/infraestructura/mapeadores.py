"""Mapeador de infraestructura: agregado de dominio <-> modelo SQLAlchemy.

Aísla al dominio del ORM. El repositorio usa este mapeador para ir y volver
entre Siniestro (dominio) y SiniestroDTO (persistencia).
"""
from modulos.siniestros.dominio.entidades import Siniestro, Evidencia, Actividad
from modulos.siniestros.dominio.objetos_valor import (
    PartnerId,
    Poliza,
    Monto,
    Direccion,
    EstadoSiniestro,
)
from modulos.siniestros.infraestructura.dto import SiniestroDTO


class MapeadorSiniestroDTO:
    def entidad_a_dto(self, s: Siniestro) -> SiniestroDTO:
        return SiniestroDTO(
            id=str(s.id),
            partner_id=s.partner_id.valor,
            poliza=s.poliza.numero,
            monto=s.monto.valor,
            moneda=s.monto.moneda,
            calle=s.direccion.calle if s.direccion else None,
            ciudad=s.direccion.ciudad if s.direccion else None,
            pais=s.direccion.pais if s.direccion else "CO",
            estado=s.estado.value,
            proveedor_id=s.proveedor_id,
            fecha_creacion=s.fecha_creacion,
            fecha_actualizacion=s.fecha_actualizacion,
            evidencias=[{"descripcion": e.descripcion, "url": e.url} for e in s.evidencias],
            actividades=[{"descripcion": a.descripcion} for a in s.actividades],
        )

    def dto_a_entidad(self, dto: SiniestroDTO) -> Siniestro:
        import uuid

        siniestro = Siniestro(
            id=uuid.UUID(dto.id),
            partner_id=PartnerId(dto.partner_id),
            poliza=Poliza(dto.poliza),
            monto=Monto(dto.monto, dto.moneda),
            direccion=Direccion(dto.calle, dto.ciudad, dto.pais),
            estado=EstadoSiniestro(dto.estado),
            proveedor_id=dto.proveedor_id,
            evidencias=[Evidencia(descripcion=e["descripcion"], url=e["url"])
                        for e in (dto.evidencias or [])],
            actividades=[Actividad(descripcion=a["descripcion"])
                         for a in (dto.actividades or [])],
        )
        siniestro._fecha_creacion = dto.fecha_creacion
        siniestro._fecha_actualizacion = dto.fecha_actualizacion
        return siniestro
