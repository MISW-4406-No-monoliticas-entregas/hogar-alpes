"""Traductor del partner Seguros Alpes.

Formato de ejemplo (dirección estructurada, monto plano):
{
  "numeroReclamo": "SA-2026-001",
  "poliza": "POL-9",
  "montoEstimado": 500000,
  "moneda": "COP",
  "direccion": {"calle": "Cra 7 # 1-2", "ciudad": "Bogota", "pais": "CO"}
}
"""
from modulos.sincronizaciones.aplicacion.dto import SiniestroCanonico
from modulos.sincronizaciones.aplicacion.traductores.base import (
    Traductor,
    ErrorTraduccion,
)


class TraductorSegurosAlpes(Traductor):
    def traducir(self, partner_id: str, payload: dict) -> SiniestroCanonico:
        try:
            direccion = payload.get("direccion") or {}
            return SiniestroCanonico(
                partner_id=partner_id,
                id_externo=str(payload["numeroReclamo"]),
                poliza=str(payload["poliza"]),
                monto=float(payload["montoEstimado"]),
                moneda=payload.get("moneda", "COP"),
                calle=direccion.get("calle"),
                ciudad=direccion.get("ciudad"),
                pais=direccion.get("pais", "CO"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ErrorTraduccion(f"Payload de Seguros Alpes inválido: {exc}") from exc
