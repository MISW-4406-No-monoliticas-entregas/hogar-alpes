"""Reglas de negocio del agregado Sincronizacion."""
from dataclasses import dataclass

from seedwork.dominio.reglas import ReglaNegocio
from modulos.sincronizaciones.dominio.objetos_valor import PartnerId, IdExterno


@dataclass
class ElPartnerYElIdExternoSonObligatorios(ReglaNegocio):
    partner_id: PartnerId | None = None
    id_externo: IdExterno | None = None

    def __init__(self, partner_id, id_externo,
                 mensaje="La sincronización requiere partner_id e id_externo"):
        super().__init__(mensaje)
        self.partner_id = partner_id
        self.id_externo = id_externo

    def es_valido(self) -> bool:
        return (
            self.partner_id is not None and bool(self.partner_id.valor.strip())
            and self.id_externo is not None and bool(self.id_externo.valor.strip())
        )
