#!/usr/bin/env python3
"""Demo end-to-end de la transaccion larga completa: S9 -> S2 -> S10 -> S7.

Corre contra el `docker compose up` local (los 4 servicios + Pulsar deben
estar arriba). Solo usa la libreria estandar de Python (sin pip install):
- HTTP directo con urllib para S9/S2/S10/S7 (los pasos que la rubrica permite
  hacer por HTTP: registrar el siniestro del partner y las consultas GET).
- `docker compose exec <servicio> python <su-propio-script>` para publicar
  los comandos reales en comandos.reglas y comandos.matching -- Postman/Newman
  no hablan Pulsar, y estos dos pasos SI tienen que pasar por el topico (no
  hay atajo HTTP para AsignarProveedor en S7, a proposito). Reutiliza las
  herramientas que ya trae cada servicio (tools/publicar_comando.py en S10,
  scripts/publicar_prueba.py en S7) en vez de reimplementar sus esquemas Avro
  aqui.

Uso, desde la raiz del repositorio (con el compose ya levantado):
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

S9 = "http://localhost:8001"
S2 = "http://localhost:8000"
S10 = "http://localhost:8002"
S7 = "http://localhost:8003"

PARTNER = "seguros-alpes"


# --------------------------------------------------------------------------
# HTTP directo (sin dependencias externas)
# --------------------------------------------------------------------------

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


def _esperar(descripcion: str, intento_fn, intentos: int = 15, espera_seg: float = 1.0):
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


# --------------------------------------------------------------------------
# Paso 1-2: S9 registra, S2 proyecta (HTTP real)
# --------------------------------------------------------------------------

def registrar_siniestro(poliza: str, monto: float) -> Optional[str]:
    _titulo(f"S9 -> POST /partners/{PARTNER}/siniestros (poliza {poliza})")
    cuerpo = {
        "numeroReclamo": f"SA-{poliza}",
        "poliza": poliza,
        "montoEstimado": monto,
        "moneda": "COP",
        "direccion": {"calle": "Cra 7 # 1-2", "ciudad": "Bogota", "pais": "CO"},
    }
    status, resp = _http("POST", f"{S9}/partners/{PARTNER}/siniestros", cuerpo)
    print(f"  -> {status} {resp}")
    if status != 202:
        print("  [ERROR] S9 no aceptó el siniestro")
        return None
    return resp["id_sincronizacion"]


def buscar_id_siniestro(poliza: str) -> Optional[str]:
    def intento():
        status, resp = _http("GET", f"{S2}/partners/{PARTNER}/siniestros")
        if status != 200:
            return None
        return next((fila for fila in resp if fila.get("poliza") == poliza), None)

    fila = _esperar(f"S2 -> proyección de la póliza {poliza}", intento)
    if fila:
        print(f"  S2 ya lo proyectó: id_siniestro={fila['id_siniestro']} estado={fila['estado']}")
        return fila["id_siniestro"]
    return None


# --------------------------------------------------------------------------
# Paso 3: S10 valida (comando real por comandos.reglas)
# --------------------------------------------------------------------------

def publicar_validar_siniestro(id_siniestro: str, monto: float, servicio: str, zona: str):
    _titulo("S10 <- comandos.reglas: ValidarSiniestro (tópico real, vía tools/publicar_comando.py)")
    cmd = [
        "docker", "compose", "exec", "-T", "reglas", "python",
        "tools/publicar_comando.py", id_siniestro, PARTNER, str(monto), servicio, zona,
    ]
    print("  $", " ".join(cmd))
    subprocess.run(cmd, check=True)


def verificar_validacion(id_siniestro: str) -> Optional[dict]:
    def intento():
        status, resp = _http("GET", f"{S10}/partners/{PARTNER}/validaciones")
        if status != 200:
            return None
        return next((fila for fila in resp if fila.get("id_siniestro") == id_siniestro), None)

    fila = _esperar(f"S10 -> validación de {id_siniestro}", intento)
    if fila:
        print(f"  Resultado: {fila['resultado']} ({fila['motivo']})")
    return fila


# --------------------------------------------------------------------------
# Paso 4: S7 asigna proveedor (comando real por comandos.matching)
# --------------------------------------------------------------------------

def publicar_asignar_proveedor(id_siniestro: str, servicio: str, zona: str):
    _titulo("S7 <- comandos.matching: AsignarProveedor (tópico real, vía scripts/publicar_prueba.py)")
    cmd = [
        "docker", "compose", "exec", "-T", "matching", "python",
        "scripts/publicar_prueba.py", "asignar", id_siniestro, servicio, zona,
    ]
    print("  $", " ".join(cmd))
    subprocess.run(cmd, check=True)


def verificar_asignacion(id_siniestro: str) -> Optional[dict]:
    def intento():
        status, resp = _http("GET", f"{S7}/asignaciones/{id_siniestro}")
        return resp if status == 200 else None

    fila = _esperar(f"S7 -> asignación de {id_siniestro}", intento)
    if fila:
        proveedor = fila.get("nombre_proveedor") or "(sin proveedor)"
        print(f"  Estado: {fila['estado']} - proveedor: {proveedor}")
    return fila


def liberar_proveedor_si_quedo_asignado(id_siniestro: str, asignacion: Optional[dict]):
    """Libera el proveedor al terminar el caso, para que el demo sea repetible.

    La semilla de S7 solo trae un proveedor disponible por servicio/zona; sin
    esto, correr el script una segunda vez ya no encontraría cobertura.
    """
    if not asignacion or asignacion.get("estado") != "ASIGNADA":
        return
    proveedor_id = asignacion.get("proveedor_id")
    _titulo(f"S7 <- comandos.matching: LiberarProveedor (limpieza, deja el proveedor libre de nuevo)")
    cmd = [
        "docker", "compose", "exec", "-T", "matching", "python",
        "scripts/publicar_prueba.py", "liberar", id_siniestro, proveedor_id,
    ]
    print("  $", " ".join(cmd))
    subprocess.run(cmd, check=True)


# --------------------------------------------------------------------------
# Orquestación de un caso completo
# --------------------------------------------------------------------------

def correr_caso(nombre: str, poliza: str, monto: float, servicio: str, zona: str) -> dict:
    print(f"\n{'#' * 72}\n CASO: {nombre}\n{'#' * 72}")
    resultado = {"caso": nombre, "poliza": poliza}

    if not registrar_siniestro(poliza, monto):
        resultado["estado"] = "FALLÓ EN S9"
        return resultado

    id_siniestro = buscar_id_siniestro(poliza)
    if not id_siniestro:
        resultado["estado"] = "FALLÓ EN S2 (no llegó a la proyección)"
        return resultado
    resultado["id_siniestro"] = id_siniestro

    publicar_validar_siniestro(id_siniestro, monto, servicio, zona)
    validacion = verificar_validacion(id_siniestro)
    resultado["reglas"] = validacion["resultado"] if validacion else "SIN RESPUESTA"

    publicar_asignar_proveedor(id_siniestro, servicio, zona)
    asignacion = verificar_asignacion(id_siniestro)
    resultado["matching"] = asignacion["estado"] if asignacion else "SIN RESPUESTA"
    resultado["proveedor"] = asignacion.get("nombre_proveedor") if asignacion else None

    liberar_proveedor_si_quedo_asignado(id_siniestro, asignacion)

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
        print(f"    id_siniestro  : {r.get('id_siniestro', '-')}")
        print(f"    S10 (reglas)  : {r.get('reglas', '-')}")
        print(f"    S7 (matching) : {r.get('matching', '-')} ({r.get('proveedor') or 'sin proveedor'})")
        if r["estado"] != "OK":
            hubo_falla = True
            print(f"    [FALLÓ]       : {r['estado']}")

    sys.exit(1 if hubo_falla else 0)


if __name__ == "__main__":
    main()
