#!/usr/bin/env python3
"""Demo end-to-end de la transaccion larga vía el orquestador (S4) y el BFF.

Desde que existe `POST /sagas` en S4, todo el flujo es HTTP puro: ya no hace
falta publicar nada a mano en un tópico (a diferencia de la Entrega 4). Solo
usa la librería estándar de Python (sin `pip install`).

Uso, desde la raíz del repositorio (con `docker compose up` ya levantado):
    python postman/demo.py
"""
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

# La consola de Windows no siempre usa UTF-8 por defecto y desfigura tildes/ñ.
for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

ORQUESTADOR = "http://localhost:8005"
BFF = "http://localhost:8004"
PARTNER = "seguros-alpes"


def _http(metodo: str, url: str, cuerpo: Optional[dict] = None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    encabezados = {"Content-Type": "application/json"} if datos else {}
    peticion = urllib.request.Request(url, data=datos, method=metodo, headers=encabezados)
    try:
        with urllib.request.urlopen(peticion, timeout=10) as resp:
            crudo = resp.read()
            return resp.status, (json.loads(crudo) if crudo else {})
    except urllib.error.HTTPError as exc:
        crudo = exc.read()
        return exc.code, (json.loads(crudo) if crudo else {})
    except urllib.error.URLError as exc:
        print(f"  [ERROR] no se pudo conectar a {url}: {exc}")
        return None, {}


def _esperar(descripcion: str, intento_fn, intentos: int = 20, espera_seg: float = 0.5):
    """Reintenta intento_fn() hasta que devuelva algo verdadero, o se agoten los intentos."""
    for _ in range(intentos):
        resultado = intento_fn()
        if resultado:
            return resultado
        time.sleep(espera_seg)
    print(f"  [TIMEOUT] {descripcion}")
    return None


def _titulo(texto: str):
    print(f"\n=== {texto} ===")


def iniciar_saga(poliza: str, monto: float, servicio: str, zona: str) -> Optional[str]:
    _titulo(f"S4 <- POST /sagas (póliza {poliza}, {servicio}/{zona})")
    cuerpo = {
        "partner_id": PARTNER,
        "poliza": poliza,
        "monto": monto,
        "moneda": "COP",
        "servicio": servicio,
        "zona": zona,
        "direccion": {"calle": "Cra 7 # 1-2", "ciudad": "Bogota", "pais": "CO"},
    }
    status, resp = _http("POST", f"{ORQUESTADOR}/sagas", cuerpo)
    print(f"  -> {status} {resp}")
    if status != 202:
        print("  [ERROR] el orquestador no aceptó la saga")
        return None
    return resp["id_saga"]


def esperar_saga_terminal(id_saga: str) -> Optional[dict]:
    def intento():
        status, resp = _http("GET", f"{ORQUESTADOR}/sagas/por-id/{id_saga}")
        if status != 200:
            return None
        return resp if resp.get("paso_actual") in ("COMPLETADA", "COMPENSADA") else None

    saga = _esperar(f"S4 -> saga {id_saga} en paso terminal", intento)
    if saga:
        print(
            f"  paso_actual={saga['paso_actual']} estado={saga['estado']} "
            f"siniestro_id={saga['siniestro_id']}"
        )
    return saga


def verificar_via_bff(id_siniestro: str):
    _titulo(f"BFF -> vista unificada del siniestro {id_siniestro}")
    status, estado = _http("GET", f"{BFF}/siniestros/{id_siniestro}/estado")
    print(f"  GET /siniestros/{id_siniestro}/estado -> {status} paso_actual={estado.get('paso_actual')}")
    status, asignacion = _http("GET", f"{BFF}/siniestros/{id_siniestro}/asignacion")
    proveedor = asignacion.get("nombre_proveedor") if isinstance(asignacion, dict) else None
    print(f"  GET /siniestros/{id_siniestro}/asignacion -> {status} estado={asignacion.get('estado')} proveedor={proveedor}")


def liberar_proveedor_si_quedo_asignado(id_siniestro: str, saga: dict):
    """Limpieza para que el demo sea repetible: la semilla de S7 solo trae un
    proveedor disponible por servicio/zona, así que sin esto una segunda
    corrida del caso "con cobertura" ya no encontraría cobertura. En un
    sistema real esto NO pasa solo -- una saga COMPLETADA se queda así; esto
    es una compensación manual de conveniencia, igual que un operador
    liberando un recurso de prueba."""
    proveedor_id = saga.get("proveedor_id")
    if saga.get("paso_actual") != "COMPLETADA" or not proveedor_id:
        return
    _titulo("(limpieza) liberando el proveedor para que el demo sea repetible")
    cmd = [
        "docker", "compose", "exec", "-T", "matching", "python",
        "scripts/publicar_prueba.py", "liberar", id_siniestro, proveedor_id,
    ]
    print("  $", " ".join(cmd))
    subprocess.run(cmd, check=True)


def correr_caso(nombre: str, poliza: str, monto: float, servicio: str, zona: str) -> dict:
    print(f"\n{'#' * 72}\n CASO: {nombre}\n{'#' * 72}")
    resultado = {"caso": nombre, "poliza": poliza}

    id_saga = iniciar_saga(poliza, monto, servicio, zona)
    if not id_saga:
        resultado["estado"] = "FALLÓ AL INICIAR"
        return resultado
    resultado["id_saga"] = id_saga

    saga = esperar_saga_terminal(id_saga)
    if not saga:
        resultado["estado"] = "TIMEOUT ESPERANDO LA SAGA"
        return resultado
    resultado["id_siniestro"] = saga["siniestro_id"]
    resultado["paso_actual"] = saga["paso_actual"]
    resultado["saga_estado"] = saga["estado"]
    resultado["proveedor"] = saga.get("proveedor_id")
    resultado["motivo_fallo"] = saga.get("motivo_fallo")

    verificar_via_bff(saga["siniestro_id"])
    liberar_proveedor_si_quedo_asignado(saga["siniestro_id"], saga)

    resultado["estado"] = "OK"
    return resultado


def main():
    marca = int(time.time())
    resultados = [
        correr_caso(
            "Con cobertura de proveedor (plomeria / bogota-norte)",
            poliza=f"POL-DEMO-COBERTURA-{marca}",
            monto=500000.0,
            servicio="plomeria",
            zona="bogota-norte",
        ),
        correr_caso(
            "Sin cobertura de proveedor (carpinteria / bogota-norte)",
            poliza=f"POL-DEMO-SINCOBERTURA-{marca}",
            monto=300000.0,
            servicio="carpinteria",
            zona="bogota-norte",
        ),
    ]

    print(f"\n{'=' * 72}\n RESUMEN\n{'=' * 72}")
    hubo_falla = False
    for r in resultados:
        print(f"\n- {r['caso']}")
        print(f"    póliza        : {r['poliza']}")
        print(f"    id_saga       : {r.get('id_saga', '-')}")
        print(f"    id_siniestro  : {r.get('id_siniestro', '-')}")
        print(f"    paso_actual   : {r.get('paso_actual', '-')} (saga {r.get('saga_estado', '-')})")
        if r.get("proveedor"):
            print(f"    proveedor     : {r['proveedor']}")
        if r.get("motivo_fallo"):
            print(f"    motivo_fallo  : {r['motivo_fallo']}")
        if r["estado"] != "OK":
            hubo_falla = True
            print(f"    [FALLÓ]       : {r['estado']}")

    sys.exit(1 if hubo_falla else 0)


if __name__ == "__main__":
    main()
