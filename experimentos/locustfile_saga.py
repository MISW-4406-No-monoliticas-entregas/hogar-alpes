"""Carga por el CAMINO DE SAGA (orquestador S4) para el escenario E3.

A diferencia de locustfile.py (que ejerce la ingesta de partners por el BFF->S9),
este pega directo a `POST /sagas` del orquestador, que es lo que arranca la
transacción larga: RegistrarSiniestro -> ValidarSiniestro -> AsignarProveedor,
con Saga Log. Se usa para E3 (disponibilidad): con sagas en vuelo se mata una
réplica de S2 y se verifica con SQL que el Saga Log no deja huérfanas.

La mezcla incluye camino feliz y camino de compensación para que el Saga Log
muestre COMPLETADA y COMPENSADA:
- plomeria/bogota-norte  -> hay proveedor -> COMPLETADA
- carpinteria/bogota-norte-> sin proveedor -> COMPENSADA (compensación)

Uso (host = orquestador):

    locust -f experimentos/locustfile_saga.py --host http://localhost:8005 \
        --headless -u 200 -r 40 -t 4m --csv experimentos/resultados/e3
"""
import uuid

from locust import HttpUser, between, task

# (servicio, zona, desenlace_esperado)
CASO_FELIZ = ("plomeria", "bogota-norte")
CASO_COMPENSA = ("carpinteria", "bogota-norte")


def _payload(servicio: str, zona: str) -> dict:
    ref = uuid.uuid4().hex[:12]
    return {
        "partner_id": "seguros-alpes",
        "poliza": f"POL-E3-{ref}",
        "monto": 500000,
        "moneda": "COP",
        "servicio": servicio,
        "zona": zona,
        "direccion": {"calle": "Cra 7 # 1-2", "ciudad": "Bogota", "pais": "CO"},
    }


class UsuarioSaga(HttpUser):
    """Arranca sagas contra el orquestador y consulta su progreso."""

    wait_time = between(0.2, 0.8)

    def on_start(self):
        self._sagas: list[str] = []
        self._n = 0

    @task(7)
    def iniciar_saga_feliz(self):
        """POST /sagas camino feliz -> debe terminar en COMPLETADA."""
        cuerpo = _payload(*CASO_FELIZ)
        with self.client.post(
            "/sagas", json=cuerpo, name="POST /sagas (feliz)", catch_response=True
        ) as r:
            if r.status_code == 202:
                dato = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
                if dato.get("id_saga"):
                    self._sagas.append(dato["id_saga"])
                    self._sagas = self._sagas[-50:]
                r.success()
            else:
                r.failure(f"POST /sagas -> {r.status_code}")

    @task(3)
    def iniciar_saga_compensa(self):
        """POST /sagas sin cobertura -> debe terminar en COMPENSADA."""
        cuerpo = _payload(*CASO_COMPENSA)
        with self.client.post(
            "/sagas", json=cuerpo, name="POST /sagas (compensa)", catch_response=True
        ) as r:
            if r.status_code == 202:
                r.success()
            else:
                r.failure(f"POST /sagas -> {r.status_code}")

    @task(2)
    def consultar_saga(self):
        """GET /sagas/por-id/<id>: progreso de la transacción larga."""
        if not self._sagas:
            return
        id_saga = self._sagas[-1]
        with self.client.get(
            f"/sagas/por-id/{id_saga}",
            name="GET /sagas/por-id/[id]",
            catch_response=True,
        ) as r:
            if r.status_code in (200, 404):
                r.success()
            else:
                r.failure(f"GET saga -> {r.status_code}")
