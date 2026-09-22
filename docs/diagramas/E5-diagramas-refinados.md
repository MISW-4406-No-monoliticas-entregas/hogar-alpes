# Diagramas refinados — Entrega 5

Refinamiento de los diagramas de la Entrega 1 (mapa de contexto TO-BE) y la
Entrega 2 (puntos de vista), **con base en los resultados de la experimentación**
de la Entrega 5. Cada diagrama está en Mermaid (lo renderiza GitHub y
[mermaid.live](https://mermaid.live) para capturar/exportar).

---

## 1. Mapa de contexto TO-BE (refinado)

**Qué cambió respecto a la Entrega 1 y por qué:**
- Se agregan dos contextos que introdujo la Entrega 5: el **Orquestador de Sagas
  (S4)** con su **Saga Log**, y el **BFF** como capa de entrada síncrona.
- La comunicación entre S2/S10/S7 deja de ser "solo log" (E4) y pasa a ser una
  **saga orquestada**: S4 coordina los pasos y reacciona a los eventos.
- Justificación (experimentación): la **orquestación** se eligió sobre coreografía
  porque el Saga Log —que E3 usó como evidencia de que no quedan transacciones
  huérfanas— es el rol natural de un orquestador centralizado.

```mermaid
flowchart TD
    Cliente["Cliente / Tutor<br/>(HTTP síncrono)"] --> BFF
    Partner["Sistemas de Partner<br/>(externo · B2B2C)"] -->|POST /partners/&lt;id&gt;/siniestros| S9

    subgraph POC["hogar-alpes / siniestros-b2b2c  (desplegado en GCP)"]
        BFF["BFF<br/>(API REST de agregación)"]
        S4["S4 Orquestador<br/>(Saga)"]
        SL[("Saga Log<br/>PostgreSQL")]
        S9["S9 Integraciones<br/>(ACL · CRUD)"]
        S2["S2 Siniestros<br/>(Event Sourcing + CQRS)"]
        S10["S10 Reglas<br/>(CRUD)"]
        S7["S7 Matching<br/>(CRUD)"]

        BFF -->|consulta estado saga| S4
        BFF -->|registra / consulta| S9
        BFF -->|proyección lectura| S2
        S4 --- SL

        S4 -->|1 · RegistrarSiniestro| CS[["comandos.siniestros"]]
        CS --> S2
        S2 -->|SiniestroRegistrado| ES[["eventos.siniestros"]]
        ES --> S4

        S4 -->|2 · ValidarSiniestro| CR[["comandos.reglas"]]
        CR --> S10
        S10 -->|Aprobado / Rechazado| ER[["eventos.reglas"]]
        ER --> S4

        S4 -->|3 · AsignarProveedor| CM[["comandos.matching"]]
        CM --> S7
        S7 -->|ProveedorAsignado / SinProveedorDisponible| EM[["eventos.matching"]]
        EM --> S4

        S4 -. compensación .-> CS
    end
```

---

## 2. Punto de vista — Despliegue (refinado)

**Qué cambió y por qué:**
- Se reemplaza el diagrama local por el **despliegue real en GCP**: una VM con un
  **cluster Pulsar de verdad** (zookeeper + 2 brokers + 2 bookies), los 6 servicios
  y 5 PostgreSQL.
- Justificación (experimentación): **E3** demostró disponibilidad tumbando un
  **broker** con carga y sin pérdida — eso exige ≥2 brokers, por eso el cluster y
  no un Pulsar standalone.

```mermaid
flowchart TB
    Internet(("Internet<br/>Tutor / Partners")) -->|8004 BFF · 8005 Saga| FW{{"Firewall GCP<br/>tcp 8000-8005, 8080/81"}}
    subgraph VM["GCE VM e2-standard-4 · Debian + Docker"]
        subgraph PULSAR["Cluster Apache Pulsar"]
            ZK["Zookeeper"]
            BR1["Broker 1"]
            BR2["Broker 2"]
            BK1["Bookie 1"]
            BK2["Bookie 2"]
        end
        subgraph SVC["Microservicios (Flask)"]
            BFF["BFF :8004"]
            ORQ["S4 Orquestador :8005"]
            S2["S2 :8000"]
            S9["S9 :8001"]
            S10["S10 :8002"]
            S7["S7 :8003"]
        end
        subgraph PG["PostgreSQL (uno por servicio)"]
            DB2[("siniestros")]
            DB9[("integraciones")]
            DB10[("reglas")]
            DB7[("matching")]
            DB4[("orquestador · saga_log")]
        end
        SVC -->|pulsar://6650| PULSAR
        ORQ --- DB4
        S2 --- DB2
        S9 --- DB9
        S10 --- DB10
        S7 --- DB7
    end
    FW --> SVC
```

---

## 3. Punto de vista — Procesos / Saga (refinado)

**Qué cambió y por qué:**
- Se agrega la **transacción larga** (no existía en E2): el flujo orquestado con su
  **camino feliz** y su **camino de compensación**, y el registro en el Saga Log.
- Justificación (experimentación): la máquina de estados
  `INICIADA → VALIDANDO → ASIGNANDO → COMPLETADA` (o `COMPENSANDO → COMPENSADA`) es
  la que E3 y las pruebas con IA verificaron que **siempre llega a un estado
  terminal** (0 huérfanas), incluso al caer un broker.

```mermaid
sequenceDiagram
    participant C as Cliente/BFF
    participant S4 as S4 Orquestador
    participant SL as Saga Log
    participant S2 as S2 Siniestros
    participant S10 as S10 Reglas
    participant S7 as S7 Matching

    C->>S4: POST /sagas (partner, poliza, servicio, zona)
    S4->>SL: crea saga (PENDIENTE/EN_CURSO)
    S4->>S2: RegistrarSiniestro
    S2-->>S4: SiniestroRegistrado
    S4->>SL: INICIADA → VALIDANDO
    S4->>S10: ValidarSiniestro
    S10-->>S4: Aprobado
    S4->>SL: VALIDANDO → ASIGNANDO
    S4->>S7: AsignarProveedor

    alt Hay proveedor (camino feliz)
        S7-->>S4: ProveedorAsignado
        S4->>SL: ASIGNANDO → COMPLETADA (OK)
    else Sin proveedor (compensación)
        S7-->>S4: SinProveedorDisponible
        S4->>SL: COMPENSANDO → COMPENSADA (FALLIDO)
        S4->>S2: (compensación) Rechazar/Liberar
    end
```

---

## Cómo exportar para el documento

1. Abrir [mermaid.live](https://mermaid.live), pegar el bloque, **Export → PNG/SVG**.
2. O verlos renderizados en GitHub (este archivo) y capturar pantalla.
