"""Traductor del partner Banco Andes.

Formato de ejemplo, DELIBERADAMENTE distinto (monto anidado con moneda, dirección
como cadena única "calle, ciudad, pais", otros nombres de campo):
{
  "ref": "BA-778",
  "policy_number": "POL-12",
  "amount": {"value": 1200000, "currency": "COP"},
  "address": "Calle 1 # 2-3, Bogota, CO"
}
"""
from modulos.sincronizaciones.aplicacion.dto import SiniestroCanonico
from modulos.sincronizaciones.aplicacion.traductores.base import (
    Traductor,
    ErrorTraduccion,
)


class TraductorBancoAndes(Traductor):
    def traducir(self, partner_id: str, payload: dict) -> SiniestroCanonico:
        try:
            amount = payload.get("amount") or {}
            partes = [p.strip() for p in str(payload["address"]).split(",")]
            calle = partes[0] if len(partes) > 0 else None
            ciudad = partes[1] if len(partes) > 1 else None
            pais = partes[2] if len(partes) > 2 else "CO"
            return SiniestroCanonico(
                partner_id=partner_id,
                id_externo=str(payload["ref"]),
                poliza=str(payload["policy_number"]),
                monto=float(amount["value"]),
                moneda=amount.get("currency", "COP"),
                calle=calle,
                ciudad=ciudad,
                pais=pais,
            )
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            raise ErrorTraduccion(f"Payload de Banco Andes inválido: {exc}") from exc
