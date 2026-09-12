# S9 — Integraciones Partners

ACL (Anti-Corruption Layer) de entrada del dominio B2B2C. Recibe los siniestros
que envían los partners en **su propio formato**, los traduce al modelo canónico
y publica el comando `RegistrarSiniestro` al dominio. No tiene reglas de negocio
de partner (eso es S10) ni autenticación.

## Flujo

```
POST /partners/<partner_id>/siniestros  (HTTP, formato propio del partner)
   -> Traductor(partner_id).traducir()  -> SiniestroCanonico          (ACL)
   -> regla idempotencia (partner_id + id_externo)                    (dominio)
   -> persistir Sincronizacion (estado PUBLICADA)                     (BD propia)
   -> comando RegistrarSiniestro  -> comandos.siniestros              (a S2)
   -> evento  SiniestroSincronizado -> eventos.partners              (integración)
```

Es la **única entrada HTTP externa** del sistema. S9 **no consume** del broker.

## Traductores por partner (modificabilidad, escenario 4)

`modulos/sincronizaciones/aplicacion/traductores/`: una clase por partner que
convierte su JSON al canónico. Dos formatos deliberadamente distintos:

- `seguros-alpes`: dirección estructurada, monto plano (`montoEstimado`).
- `banco-andes`: monto anidado (`amount.value/currency`), dirección como cadena.

Agregar un partner = agregar una clase `Traductor` y registrarla en
`registro.py`. No se toca nada más.

## Topología y esquemas

| Salida | Tópico | Esquema |
|---|---|---|
| Comando | `comandos.siniestros` | `ComandoRegistrarSiniestro` **copiado tal cual** de Siniestros (el dueño del esquema del comando es quien lo consume) |
| Evento | `eventos.partners` | `SiniestroSincronizado` (propio de S9) |

## Base de datos

`sincronizaciones(id, partner_id, id_externo, id_siniestro, estado, recibido_en,
publicado_en)` con índice único `(partner_id, id_externo)` = idempotencia de
negocio a nivel de BD. `id_siniestro` se llena en la E5 (saga).

## API

| Método | Ruta | Código |
|---|---|---|
| `POST` | `/partners/<partner_id>/siniestros` | 202 (`id_sincronizacion`) / 409 duplicado / 400 partner o payload inválido |
| `GET`  | `/sincronizaciones/<id>` | 200 / 404 |
| `GET`  | `/partners/<partner_id>/sincronizaciones` | 200 |

## Pruebas

```bash
cd src/integraciones && pip install -r requirements.txt && pytest
```

Cubre las reglas del agregado y los dos traductores.
