# Despliegue en GCP

Despliega el POC en una VM de **Google Compute Engine** con el cluster real de
Pulsar (`docker-compose.cluster.yml`).

## Por qué una VM (y no Cloud Run / GKE)

- Los consumidores de Pulsar son procesos **siempre encendidos**; Cloud Run
  escala a cero y no sirve para suscriptores de larga vida.
- Operar GKE en pocos días era el mayor riesgo del plan. En producción el destino
  es **GKE con Pulsar multi-zona** (PS-04).
- `e2-standard-4` (4 vCPU / 16 GB) ≈ USD 0,13/h; se apaga cuando no se usa.

## Pasos

```bash
# Requisito: gcloud autenticado (gcloud auth login) y un proyecto con créditos.
export GCP_PROJECT=<tu-proyecto>

# 1. Crea VM (Debian 12 + Docker) y el firewall (APIs 8000-8005, incl. BFF 8004 y orquestador 8005; admin Pulsar 8080/8081)
bash infra/gcp/crear_vm.sh

# 2. Clona el repo en la VM y levanta el cluster
bash infra/gcp/desplegar.sh
```

Variables opcionales: `GCP_ZONE` (def. `us-central1-a`), `GCP_VM`
(def. `hogar-alpes-poc`), `GCP_MACHINE` (def. `e2-standard-4`), `FIREWALL_SOURCE`
(def. `0.0.0.0/0` — **restríngelo a tu IP** en un entorno real), `REPO_BRANCH`.

## Seguridad

- **Cero credenciales en el repo.** Los compose traen valores de desarrollo; en la
  VM, las credenciales de producción van en un `.env` fuera de git (ver
  [`.env.example`](../../.env.example)). El `docker-compose.cluster.yml` lee las
  contraseñas de BD por variables `${DB_*_PASSWORD}`.
- Los puertos binarios de Pulsar (6650/6651) **no** se abren en el firewall: los
  únicos clientes son los servicios, dentro de la VM.

## Apagar (para no gastar créditos)

```bash
gcloud compute instances stop hogar-alpes-poc --zone=us-central1-a
# y para borrarla del todo:
gcloud compute instances delete hogar-alpes-poc --zone=us-central1-a
```
