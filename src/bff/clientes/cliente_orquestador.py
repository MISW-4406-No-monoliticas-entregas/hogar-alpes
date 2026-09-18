"""Cliente hacia el orquestador de sagas (S4) y su Saga Log.

ESTADO: el orquestador NO existe todavía en este repositorio (se construye en
una rama paralela). Este cliente queda listo para consumir el contrato
esperado en cuanto exista; mientras `ORQUESTADOR_URL` esté vacía, la API del
BFF responde 501 con un mensaje explícito.

Contrato esperado (a confirmar con el dueño de S4 al integrar):

    GET /sagas/<id_siniestro>
    200 {
      "id_siniestro": "...",
      "paso_actual":  "RegistrarSiniestro" | "ValidarSiniestro" | "AsignarProveedor",
      "estado":       "EN_PROGRESO" | "COMPLETADA" | "COMPENSADA" | "FALLIDA",
      "historial": [
        {"paso": "RegistrarSiniestro", "estado": "OK", "fecha": "...", "detalle": "..."},
        ...
      ]
    }
    404 si no hay saga para ese siniestro.

Si S4 define otra ruta o forma, el único cambio es la ruta de `obtener_saga`:
el BFF devuelve el cuerpo tal cual, sin reinterpretarlo.
"""
from clientes.base import ClienteHTTP, Respuesta


class ClienteOrquestador(ClienteHTTP):
    nombre = "S4 Orquestador"

    def obtener_saga(self, id_siniestro: str) -> Respuesta:
        """GET /sagas/<id_siniestro> -> estado consolidado de la transacción larga."""
        return self.get(f"/sagas/{id_siniestro}")
