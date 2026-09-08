"""Configuración del broker vía la API de administración de Pulsar."""
import json
import logging
import time
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)


def _put(url: str, cuerpo) -> None:
    datos = json.dumps(cuerpo).encode("utf-8")
    peticion = urllib.request.Request(
        url, data=datos, method="PUT",
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(peticion, timeout=5).read()


def configurar_namespace_multiesquema(
    admin_url: str, tenant: str = "public", namespace: str = "default",
    intentos: int = 10, espera_seg: int = 3,
) -> None:
    base = f"{admin_url}/admin/v2/namespaces/{tenant}/{namespace}"
    for intento in range(1, intentos + 1):
        try:
            _put(f"{base}/schemaCompatibilityStrategy", "ALWAYS_COMPATIBLE")
            logger.info(
                "Namespace %s/%s configurado para multiples esquemas por topico",
                tenant, namespace,
            )
            return
        except (urllib.error.URLError, OSError) as exc:
            logger.warning(
                "Broker no disponible para configurar esquemas (intento %s/%s): %s",
                intento, intentos, exc,
            )
            time.sleep(espera_seg)
    logger.error("No se pudo configurar la estrategia de esquemas del namespace")
