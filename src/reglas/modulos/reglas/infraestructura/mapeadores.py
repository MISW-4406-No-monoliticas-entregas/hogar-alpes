"""Mapeadores entre los agregados del modulo reglas y sus modelos SQLAlchemy."""
import uuid

from modulos.reglas.dominio.entidades import ReglaDePartner, Validacion
from modulos.reglas.dominio.objetos_valor import (
    Monto,
    PartnerId,
    ResultadoValidacion,
    Servicio,
    Zona,
)
from modulos.reglas.infraestructura.dto import ReglaDePartnerDTO, ValidacionDTO

SEPARADOR = ","


def _unir(valores: list[str]) -> str:
    return SEPARADOR.join(valores)


def _partir(texto: str) -> list[str]:
    return [t.strip() for t in texto.split(SEPARADOR) if t.strip()]


class MapeadorReglaDePartnerDTO:
    def entidad_a_dto(self, r: ReglaDePartner) -> ReglaDePartnerDTO:
        return ReglaDePartnerDTO(
            id=str(r.id),
            partner_id=r.partner_id.valor,
            monto_maximo=r.monto_maximo.valor,
            moneda=r.monto_maximo.moneda,
            servicios_cubiertos=_unir([s.nombre for s in r.servicios_cubiertos]),
            zonas_habilitadas=_unir([z.nombre for z in r.zonas_habilitadas]),
            activa=r.activa,
            fecha_creacion=r.fecha_creacion,
            fecha_actualizacion=r.fecha_actualizacion,
        )

    def dto_a_entidad(self, dto: ReglaDePartnerDTO) -> ReglaDePartner:
        regla = ReglaDePartner(
            id=uuid.UUID(dto.id),
            partner_id=PartnerId(dto.partner_id),
            monto_maximo=Monto(dto.monto_maximo, dto.moneda),
            servicios_cubiertos=[Servicio(s) for s in _partir(dto.servicios_cubiertos)],
            zonas_habilitadas=[Zona(z) for z in _partir(dto.zonas_habilitadas)],
            activa=dto.activa,
        )
        regla._fecha_creacion = dto.fecha_creacion
        regla._fecha_actualizacion = dto.fecha_actualizacion
        return regla


class MapeadorValidacionDTO:
    def entidad_a_dto(self, v: Validacion) -> ValidacionDTO:
        return ValidacionDTO(
            id=str(v.id),
            id_siniestro=v.id_siniestro,
            partner_id=v.partner_id.valor,
            monto=v.monto.valor,
            moneda=v.monto.moneda,
            servicio=v.servicio.nombre,
            zona=v.zona.nombre,
            resultado=v.resultado.value,
            motivo=v.motivo,
            fecha_creacion=v.fecha_creacion,
            fecha_actualizacion=v.fecha_actualizacion,
        )

    def dto_a_entidad(self, dto: ValidacionDTO) -> Validacion:
        validacion = Validacion(
            id=uuid.UUID(dto.id),
            id_siniestro=dto.id_siniestro,
            partner_id=PartnerId(dto.partner_id),
            monto=Monto(dto.monto, dto.moneda),
            servicio=Servicio(dto.servicio),
            zona=Zona(dto.zona),
            resultado=ResultadoValidacion(dto.resultado),
            motivo=dto.motivo,
        )
        validacion._fecha_creacion = dto.fecha_creacion
        validacion._fecha_actualizacion = dto.fecha_actualizacion
        return validacion
