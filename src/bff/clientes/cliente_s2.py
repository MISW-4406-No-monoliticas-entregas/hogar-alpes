"""Cliente hacia S2 Trabajos Siniestros (dueño del agregado Siniestro).

Solo consultas GET sobre la proyección `estado_siniestro`. Rutas verificadas en
src/siniestros/api/siniestros.py. Los POST de S2 son utilidades de prueba y el
BFF NO los usa: el registro entra por S9.
"""
from clientes.base import ClienteHTTP, Respuesta


class ClienteS2(ClienteHTTP):
    nombre = "S2 Siniestros"

    def obtener_siniestro(self, id_siniestro: str) -> Respuesta:
        """GET /siniestros/<id> -> 200 {id_siniestro, partner_id, estado, poliza,
        monto, moneda, proveedor_id, fecha_actualizacion} / 404."""
        return self.get(f"/siniestros/{id_siniestro}")

    def listar_siniestros_por_partner(self, partner_id: str) -> Respuesta:
        """GET /partners/<partner_id>/siniestros -> 200 [EstadoDeSiniestro]."""
        return self.get(f"/partners/{partner_id}/siniestros")
