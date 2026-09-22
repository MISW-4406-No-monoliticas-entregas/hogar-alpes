"""Carga para los escenarios de calidad de la Entrega 5 (Parte A).

Pega contra el **BFF** (entrada síncrona de negocio, camino real del partner),
que reenvía a S9 -> comandos.siniestros -> saga S4 -> S2/S10/S7.

Uso rápido (ver experimentos/README.md para E1/E2/E3):

    # baseline 1x, interactivo (UI en http://localhost:8089)
    locust -f experimentos/locustfile.py --host http://localhost:8004

    # E1 pico 4x, headless, 5 min, con reporte
    locust -f experimentos/locustfile.py --host http://localhost:8004 \
        --headless -u 400 -r 40 -t 5m \
        --csv experimentos/resultados/e1_4x --html experimentos/resultados/e1_4x.html

Métricas que reporta Locust y que alimentan el documento de resultados:
- p50/p95/p99 de "POST /siniestros" -> latencia de ACEPTACIÓN del comando (E1).
- RPS agregado -> throughput; se compara 1x vs 4x y N vs 3N réplicas.
- % de fallos -> pérdida/errores bajo carga (E3).

Idempotencia: S9 deduplica por (partner_id + id_externo). Cada request usa un
id externo único (uuid) para crear siniestros nuevos y NO chocar con 409.
"""
import uuid

from locust import HttpUser, between, task


def _payload_seguros_alpes() -> dict:
    """Formato propio del partner 'seguros-alpes' (el BFF/S9 no lo traduce aquí)."""
    ref = uuid.uuid4().hex[:12]
    return {
        "partner_id": "seguros-alpes",
        "siniestro": {
            "numeroReclamo": f"SA-{ref}",
            "poliza": f"POL-SA-{ref}",
            "montoEstimado": 500000,
            "moneda": "COP",
            "direccion": {"calle": "Cra 7 # 1-2", "ciudad": "Bogota", "pais": "CO"},
        },
    }


def _payload_banco_andes() -> dict:
    """Otro formato de partner ('banco-andes') para ejercitar el ACL de S9."""
    ref = uuid.uuid4().hex[:12]
    return {
        "partner_id": "banco-andes",
        "siniestro": {
            "ref": f"BA-{ref}",
            "policy_number": f"POL-BA-{ref}",
            "amount": {"value": 1200000, "currency": "COP"},
            "address": "Calle 1 # 2-3, Bogota, CO",
        },
    }


class UsuarioPartner(HttpUser):
    """Simula a un partner que ingesta siniestros y consulta su estado.

    La mezcla por defecto es de ingesta-pesada (el 70% del volumen del caso es
    B2B2C de partners). Para E1 lo que importa es la latencia/throughput del POST;
    las lecturas ejercitan el lado CQRS y el Saga Log.
    """

    # Piensa poco entre requests: modela ingesta automática de un partner, no un
    # humano. Sube/baja este rango para afinar la carga por usuario.
    wait_time = between(0.1, 0.5)

    def on_start(self):
        # Ids de sincronización aceptados por este usuario, para lecturas de seguimiento.
        self._sincronizaciones: list[str] = []
        self._alterna = 0

    @task(8)
    def registrar_siniestro(self):
        """POST /siniestros -> S9 (métrica central de E1: latencia de aceptación)."""
        self._alterna += 1
        cuerpo = _payload_seguros_alpes() if self._alterna % 2 else _payload_banco_andes()
        with self.client.post(
            "/siniestros", json=cuerpo, name="POST /siniestros", catch_response=True
        ) as r:
            if r.status_code == 202:
                dato = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
                id_sinc = dato.get("id_sincronizacion")
                if id_sinc:
                    # Se guarda una ventana pequeña para no crecer sin límite en memoria.
                    self._sincronizaciones.append(id_sinc)
                    self._sincronizaciones = self._sincronizaciones[-50:]
                r.success()
            elif r.status_code == 409:
                # Duplicado: no debería ocurrir con ids únicos; no es fallo del sistema.
                r.success()
            else:
                r.failure(f"POST /siniestros -> {r.status_code}")

    @task(2)
    def listar_por_partner(self):
        """GET proyección S2 (lado lectura CQRS bajo carga)."""
        partner = "seguros-alpes" if self._alterna % 2 else "banco-andes"
        self.client.get(
            f"/partners/{partner}/siniestros", name="GET /partners/[id]/siniestros"
        )

    @task(1)
    def consultar_sincronizacion(self):
        """GET /sincronizaciones/<id>: ¿S9 aceptó y publicó el registro?"""
        if not self._sincronizaciones:
            return
        id_sinc = self._sincronizaciones[-1]
        self.client.get(
            f"/sincronizaciones/{id_sinc}", name="GET /sincronizaciones/[id]"
        )

    @task(1)
    def consultar_estado_saga(self):
        """GET /siniestros/<id>/estado -> Saga Log del orquestador (E3).

        Mientras S4 no esté integrado (ORQUESTADOR_URL vacía) el BFF responde 501;
        se marca como esperado para no ensuciar la tasa de fallos del baseline.
        """
        if not self._sincronizaciones:
            return
        # Se usa el id de sincronización como correlación mientras se define el id de saga.
        id_ref = self._sincronizaciones[-1]
        with self.client.get(
            f"/siniestros/{id_ref}/estado",
            name="GET /siniestros/[id]/estado (saga)",
            catch_response=True,
        ) as r:
            if r.status_code == 501:
                r.success()  # orquestador aún no integrado; esperado en baseline
            elif r.status_code in (200, 404):
                r.success()
            else:
                r.failure(f"estado saga -> {r.status_code}")
