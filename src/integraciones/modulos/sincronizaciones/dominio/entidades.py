"""Entidades del módulo sincronizaciones: agregado Sincronizacion."""
from dataclasses import dataclass

from seedwork.dominio.entidades import AgregacionRaiz
from modulos.sincronizaciones.dominio.objetos_valor import (
    PartnerId,
    IdExterno,
    EstadoSincronizacion,
)
from modulos.sincronizaciones.dominio.eventos import SiniestroSincronizado
from modulos.sincronizaciones.dominio.reglas import (
    ElPartnerYElIdExternoSonObligatorios,
)


@dataclass
class Sincronizacion(AgregacionRaiz):
    """Agregado raíz: una recepción de siniestro desde un partner (ACL de entrada).

    id_siniestro queda pendiente hasta la E5 (cuando Siniestros confirme el registro
    vía la saga); en la E4 solo publicamos el comando y el evento.
    """
    partner_id: PartnerId = None
    id_externo: IdExterno = None
    estado: EstadoSincronizacion = None
    id_siniestro: str | None = None
    # Carga canónica que viaja al comando/evento (no se persiste columna a columna):
    _canonico: dict = None

    def sincronizar(self, canonico: dict):
        """Valida las invariantes, pasa a PUBLICADA y emite el evento de dominio."""
        self.validar_regla(
            ElPartnerYElIdExternoSonObligatorios(self.partner_id, self.id_externo)
        )
        self._canonico = canonico
        self.estado = EstadoSincronizacion.PUBLICADA
        self.agregar_evento(
            SiniestroSincronizado(
                id_sincronizacion=self.id,
                partner_id=self.partner_id.valor,
                id_externo=self.id_externo.valor,
                poliza=canonico["poliza"],
                monto=canonico["monto"],
                moneda=canonico["moneda"],
                calle=canonico["calle"],
                ciudad=canonico["ciudad"],
                pais=canonico.get("pais", "CO"),
            )
        )
