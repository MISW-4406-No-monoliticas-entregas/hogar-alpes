"""Mapeador de aplicación: DTO a objetos valor de dominio."""
from seedwork.aplicacion.mapeadores import Mapeador
from modulos.siniestros.dominio.entidades import Siniestro
from modulos.siniestros.dominio.objetos_valor import (
    PartnerId,
    Poliza,
    Monto,
    Direccion,
)
from modulos.siniestros.aplicacion.dto import SiniestroDTO


class MapeadorSiniestro(Mapeador):
    def dto_a_entidad(self, dto: SiniestroDTO) -> Siniestro:
        raise NotImplementedError

    def dto_a_objetos_valor(self, dto: SiniestroDTO):
        return dict(
            partner_id=PartnerId(dto.partner_id),
            poliza=Poliza(dto.poliza),
            monto=Monto(dto.monto, dto.moneda or "COP"),
            direccion=Direccion(dto.calle, dto.ciudad, dto.pais or "CO"),
        )

    def entidad_a_dto(self, siniestro: Siniestro) -> SiniestroDTO:
        return SiniestroDTO(
            id=str(siniestro.id),
            partner_id=siniestro.partner_id.valor,
            poliza=siniestro.poliza.numero,
            monto=siniestro.monto.valor,
            moneda=siniestro.monto.moneda,
            calle=siniestro.direccion.calle,
            ciudad=siniestro.direccion.ciudad,
            pais=siniestro.direccion.pais,
            estado=siniestro.estado.value if siniestro.estado else None,
            proveedor_id=siniestro.proveedor_id,
        )
