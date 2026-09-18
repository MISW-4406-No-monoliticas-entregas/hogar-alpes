"""Cliente hacia S9 Integraciones Partners (ACL de entrada).

Rutas verificadas en src/integraciones/api/sincronizaciones.py.
"""
from clientes.base import ClienteHTTP, Respuesta


class ClienteS9(ClienteHTTP):
    nombre = "S9 Integraciones"

    def registrar_siniestro(self, partner_id: str, payload_partner: dict) -> Respuesta:
        """POST /partners/<partner_id>/siniestros -> 202 {id_sincronizacion, estado}.

        `payload_partner` va en el formato propio del partner: la traducción al
        modelo canónico la hace S9 (es su responsabilidad como ACL), no el BFF.
        """
        return self.post(f"/partners/{partner_id}/siniestros", payload_partner)

    def obtener_sincronizacion(self, id_sincronizacion: str) -> Respuesta:
        """GET /sincronizaciones/<id> -> 200 SincronizacionDTO / 404."""
        return self.get(f"/sincronizaciones/{id_sincronizacion}")

    def listar_sincronizaciones(self, partner_id: str) -> Respuesta:
        """GET /partners/<partner_id>/sincronizaciones -> 200 [SincronizacionDTO]."""
        return self.get(f"/partners/{partner_id}/sincronizaciones")
