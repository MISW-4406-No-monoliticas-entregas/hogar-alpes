#!/usr/bin/env python3
"""P1 — Prueba property-based no-determinística sobre la saga (S4).

Genera N solicitudes de saga con servicio/zona/monto/partner ALEATORIOS y
verifica INVARIANTES de dominio (no salidas exactas), que es lo que hace válida
una prueba no-determinística. Pensada para que un agente (Claude Code) la corra,
lea el JSON de salida y diagnostique cualquier violación en términos de negocio.

Invariantes verificadas:
  I1 Terminalidad : toda saga POSTeada termina en COMPLETADA o COMPENSADA (0 huérfanas).
  I2 No pérdida   : toda saga POSTeada es recuperable por su id (0 perdidas).
  I3 Coherencia   : COMPLETADA => tiene proveedor_id ; COMPENSADA => sin proveedor y con motivo_fallo.
  I4 Integridad   : la saga refleja la póliza que se envió (round-trip sin corrupción).

Uso:
    python experimentos/pruebas_ia/invariantes.py --n 40 --host http://localhost:8005

Código de salida != 0 si algún invariante falla (apto para CI / para el agente).
"""
import argparse
import json
import random
import sys
import time
import urllib.error
import urllib.request

# Combinaciones del catálogo sembrado; la mezcla produce COMPLETADA y COMPENSADA.
SERVICIOS = ["plomeria", "electricidad", "carpinteria", "cerrajeria", "gasfiteria"]
ZONAS = ["bogota-norte", "bogota-centro", "medellin", "cali", "barranquilla"]
PARTNERS = ["seguros-alpes", "banco-andes"]
TERMINALES = {"COMPLETADA", "COMPENSADA"}


def _post(host, ruta, cuerpo):
    req = urllib.request.Request(
        host + ruta, data=json.dumps(cuerpo).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.status, json.loads(r.read() or b"{}")


def _get(host, ruta):
    try:
        with urllib.request.urlopen(host + ruta, timeout=10) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, {}


def generar_caso(i):
    """Caso aleatorio (no-determinístico). La semilla varía por corrida."""
    return {
        "partner_id": random.choice(PARTNERS),
        "poliza": f"POL-IA-{i}-{random.randint(10**6, 10**7)}",
        "monto": round(random.uniform(50_000, 5_000_000), 2),
        "moneda": "COP",
        "servicio": random.choice(SERVICIOS),
        "zona": random.choice(ZONAS),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--host", default="http://localhost:8005")
    ap.add_argument("--timeout", type=int, default=120, help="segundos de espera a terminal")
    args = ap.parse_args()

    random.seed()  # no-determinístico a propósito

    # 1) generar y POSTear
    enviados = []  # (id_saga, poliza)
    for i in range(args.n):
        caso = generar_caso(i)
        try:
            code, resp = _post(args.host, "/sagas", caso)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR POST /sagas: {e}", file=sys.stderr)
            return 2
        if code == 202 and resp.get("id_saga"):
            enviados.append((resp["id_saga"], caso["poliza"]))
        else:
            print(f"POST inesperado {code}: {resp}", file=sys.stderr)
    print(f"POSTeadas {len(enviados)}/{args.n} sagas; esperando estado terminal...")

    # 2) esperar terminalidad
    finales = {}
    t0 = time.time()
    pendientes = {sid for sid, _ in enviados}
    while pendientes and time.time() - t0 < args.timeout:
        for sid in list(pendientes):
            code, saga = _get(args.host, f"/sagas/por-id/{sid}")
            if code == 200 and saga.get("paso_actual") in TERMINALES:
                finales[sid] = saga
                pendientes.discard(sid)
        if pendientes:
            time.sleep(2)

    # 3) evaluar invariantes
    polizas = dict(enviados)
    v = {}
    v["I1_terminalidad"] = {
        "ok": len(pendientes) == 0,
        "huerfanas": len(pendientes),
        "detalle": "toda saga alcanza COMPLETADA/COMPENSADA",
    }
    recuperables = sum(1 for sid, _ in enviados if _get(args.host, f"/sagas/por-id/{sid}")[0] == 200)
    v["I2_no_perdida"] = {
        "ok": recuperables == len(enviados),
        "recuperables": recuperables, "posteadas": len(enviados),
    }
    incoherentes = []
    for sid, saga in finales.items():
        paso = saga.get("paso_actual")
        prov = saga.get("proveedor_id")
        motivo = saga.get("motivo_fallo")
        if paso == "COMPLETADA" and not prov:
            incoherentes.append({"id": sid, "por": "COMPLETADA sin proveedor_id"})
        if paso == "COMPENSADA" and prov:
            incoherentes.append({"id": sid, "por": "COMPENSADA con proveedor_id"})
        if paso == "COMPENSADA" and not motivo:
            incoherentes.append({"id": sid, "por": "COMPENSADA sin motivo_fallo"})
    v["I3_coherencia_desenlace"] = {"ok": not incoherentes, "violaciones": incoherentes[:10]}
    corruptas = [
        {"id": sid, "esperada": polizas[sid], "obtenida": saga.get("poliza")}
        for sid, saga in finales.items() if saga.get("poliza") != polizas.get(sid)
    ]
    v["I4_integridad_poliza"] = {"ok": not corruptas, "violaciones": corruptas[:10]}

    resumen = {
        "n": args.n,
        "posteadas": len(enviados),
        "terminales": len(finales),
        "desenlaces": {
            "COMPLETADA": sum(1 for s in finales.values() if s.get("paso_actual") == "COMPLETADA"),
            "COMPENSADA": sum(1 for s in finales.values() if s.get("paso_actual") == "COMPENSADA"),
        },
        "invariantes": v,
        "veredicto": "PASA" if all(x["ok"] for x in v.values()) else "FALLA",
    }
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    return 0 if resumen["veredicto"] == "PASA" else 1


if __name__ == "__main__":
    sys.exit(main())
