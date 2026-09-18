"""Cliente hacia S7 Matching de Proveedores.

Rutas verificadas en src/matching/api/matching.py.
"""
from clientes.base import ClienteHTTP, Respuesta


class ClienteS7(ClienteHTTP):
    nombre = "S7 Matching"

    def listar_proveedores(self, zona: str, servicio: str) -> Respuesta:
        """GET /proveedores?zona=&servicio= -> 200 [ProveedorHabilitadoDTO] / 400."""
        return self.get("/proveedores", params={"zona": zona, "servicio": servicio})

    def obtener_asignacion(self, id_siniestro: str) -> Respuesta:
        """GET /asignaciones/<id_siniestro> -> 200 AsignacionDTO / 404."""
        return self.get(f"/asignaciones/{id_siniestro}")
