"""Entidades del modulo reglas: agregados ReglaDePartner y Validacion."""
from dataclasses import dataclass, field

from seedwork.dominio.entidades import AgregacionRaiz
from modulos.reglas.dominio.objetos_valor import (
    Evaluacion,
    Monto,
    PartnerId,
    ResultadoValidacion,
    Servicio,
    Zona,
)
from modulos.reglas.dominio.eventos import (
    SiniestroAprobadoPorReglas,
    SiniestroRechazadoPorReglas,
)
from modulos.reglas.dominio.reglas import (
    DebeCubrirAlMenosUnServicio,
    DebeHabilitarAlMenosUnaZona,
    ElMontoEvaluadoDebeSerPositivo,
    ElMontoMaximoDebeSerPositivo,
    ElPartnerEsObligatorio,
    LaValidacionDebeReferirUnSiniestro,
)


@dataclass
class ReglaDePartner(AgregacionRaiz):
    """Lo pactado con un partner: cuanto cubre, que servicios y en que zonas."""
    partner_id: PartnerId = None
    monto_maximo: Monto = None
    servicios_cubiertos: list[Servicio] = field(default_factory=list)
    zonas_habilitadas: list[Zona] = field(default_factory=list)
    activa: bool = True

    def definir(self):
        self.validar_regla(ElPartnerEsObligatorio(self.partner_id))
        self.validar_regla(ElMontoMaximoDebeSerPositivo(self.monto_maximo))
        self.validar_regla(DebeCubrirAlMenosUnServicio(self.servicios_cubiertos))
        self.validar_regla(DebeHabilitarAlMenosUnaZona(self.zonas_habilitadas))

    def evaluar(self, monto: Monto, servicio: Servicio, zona: Zona) -> Evaluacion:
        """Aplica lo pactado y devuelve el veredicto. No muta ni emite eventos."""
        if not self.activa:
            return Evaluacion(ResultadoValidacion.RECHAZADO, "El contrato del partner no esta activo")
        if monto.moneda != self.monto_maximo.moneda:
            return Evaluacion(
                ResultadoValidacion.RECHAZADO,
                f"Moneda {monto.moneda} distinta de la pactada {self.monto_maximo.moneda}",
            )
        if monto.valor > self.monto_maximo.valor:
            return Evaluacion(
                ResultadoValidacion.RECHAZADO,
                f"Monto {monto.valor} supera el maximo cubierto {self.monto_maximo.valor}",
            )
        if servicio not in self.servicios_cubiertos:
            return Evaluacion(
                ResultadoValidacion.RECHAZADO,
                f"El servicio {servicio.nombre} no esta cubierto por el partner",
            )
        if zona not in self.zonas_habilitadas:
            return Evaluacion(
                ResultadoValidacion.RECHAZADO,
                f"La zona {zona.nombre} no esta habilitada para el partner",
            )
        return Evaluacion(ResultadoValidacion.APROBADO, "Cumple lo pactado con el partner")


@dataclass
class Validacion(AgregacionRaiz):
    """Registro inmutable del veredicto de una evaluacion sobre un siniestro."""
    id_siniestro: str = None
    partner_id: PartnerId = None
    monto: Monto = None
    servicio: Servicio = None
    zona: Zona = None
    resultado: ResultadoValidacion = None
    motivo: str = None

    def registrar(self, evaluacion: Evaluacion):
        self.validar_regla(LaValidacionDebeReferirUnSiniestro(self.id_siniestro))
        self.validar_regla(ElPartnerEsObligatorio(self.partner_id))
        self.validar_regla(ElMontoEvaluadoDebeSerPositivo(self.monto))

        self.resultado = evaluacion.resultado
        self.motivo = evaluacion.motivo

        if self.resultado == ResultadoValidacion.APROBADO:
            self.agregar_evento(
                SiniestroAprobadoPorReglas(
                    id_validacion=self.id,
                    id_siniestro=self.id_siniestro,
                    partner_id=self.partner_id.valor,
                    monto=self.monto.valor,
                    moneda=self.monto.moneda,
                    servicio=self.servicio.nombre,
                    zona=self.zona.nombre,
                    motivo=self.motivo,
                )
            )
        else:
            self.agregar_evento(
                SiniestroRechazadoPorReglas(
                    id_validacion=self.id,
                    id_siniestro=self.id_siniestro,
                    partner_id=self.partner_id.valor,
                    monto=self.monto.valor,
                    moneda=self.monto.moneda,
                    servicio=self.servicio.nombre,
                    zona=self.zona.nombre,
                    motivo=self.motivo,
                )
            )
