"""Cliente hacia S10 Reglas de Partner.

Rutas verificadas en src/reglas/api/reglas.py.
"""
from clientes.base import ClienteHTTP, Respuesta


class ClienteS10(ClienteHTTP):
    nombre = "S10 Reglas"

    def obtener_reglas(self, partner_id: str) -> Respuesta:
        """GET /partners/<partner_id>/reglas -> 200 ReglaDePartnerDTO / 404."""
        return self.get(f"/partners/{partner_id}/reglas")

    def listar_validaciones(self, partner_id: str, limite: int | None = None) -> Respuesta:
        """GET /partners/<partner_id>/validaciones?limite=N -> 200 [ValidacionDTO]."""
        params = {"limite": limite} if limite is not None else None
        return self.get(f"/partners/{partner_id}/validaciones", params=params)
