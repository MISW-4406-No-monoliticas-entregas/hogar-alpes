"""Invariantes de los agregados ReglaDePartner y Validacion."""
from dataclasses import dataclass

from seedwork.dominio.reglas import ReglaNegocio
from modulos.reglas.dominio.objetos_valor import Monto, PartnerId


@dataclass
class ElPartnerEsObligatorio(ReglaNegocio):
    partner_id: PartnerId | None = None

    def __init__(self, partner_id, mensaje="La regla debe pertenecer a un partner"):
        super().__init__(mensaje)
        self.partner_id = partner_id

    def es_valido(self) -> bool:
        return self.partner_id is not None and bool(self.partner_id.valor.strip())


@dataclass
class ElMontoMaximoDebeSerPositivo(ReglaNegocio):
    monto_maximo: Monto | None = None

    def __init__(self, monto_maximo, mensaje="El monto maximo cubierto debe ser positivo"):
        super().__init__(mensaje)
        self.monto_maximo = monto_maximo

    def es_valido(self) -> bool:
        return self.monto_maximo is not None and self.monto_maximo.valor > 0


@dataclass
class DebeCubrirAlMenosUnServicio(ReglaNegocio):
    servicios: list | None = None

    def __init__(self, servicios, mensaje="El partner debe cubrir al menos un servicio"):
        super().__init__(mensaje)
        self.servicios = servicios

    def es_valido(self) -> bool:
        return bool(self.servicios)


@dataclass
class DebeHabilitarAlMenosUnaZona(ReglaNegocio):
    zonas: list | None = None

    def __init__(self, zonas, mensaje="El partner debe habilitar al menos una zona"):
        super().__init__(mensaje)
        self.zonas = zonas

    def es_valido(self) -> bool:
        return bool(self.zonas)


@dataclass
class LaValidacionDebeReferirUnSiniestro(ReglaNegocio):
    id_siniestro: str | None = None

    def __init__(self, id_siniestro, mensaje="La validacion debe referir un siniestro"):
        super().__init__(mensaje)
        self.id_siniestro = id_siniestro

    def es_valido(self) -> bool:
        return self.id_siniestro is not None and bool(str(self.id_siniestro).strip())


@dataclass
class ElMontoEvaluadoDebeSerPositivo(ReglaNegocio):
    monto: Monto | None = None

    def __init__(self, monto, mensaje="El monto del siniestro a validar debe ser positivo"):
        super().__init__(mensaje)
        self.monto = monto

    def es_valido(self) -> bool:
        return self.monto is not None and self.monto.valor > 0
