"""Comando ReconstruirProyeccion: regenera estado_siniestro desde el event store.

Es la prueba de que el event store es la fuente de verdad: trunca las filas
afectadas de la proyección y reaplica, en orden de versión, cada evento contra
los MISMOS handlers de proyección de seguimiento que corren en línea.

Los eventos se reaplican llamando los handlers de proyección directamente (no
vía el despachador de señales): reconstruir la proyección NO debe volver a
publicar eventos de integración en Pulsar.

Entra por HTTP como utilidad admin (POST /admin/proyecciones/estado-siniestro/
reconstruir); no hace falta que entre por el broker.
"""
from dataclasses import dataclass

from seedwork.aplicacion.comandos import Comando, ComandoHandler, ejecutar_comando
from config.db import SessionLocal
from modulos.seguimiento.aplicacion import handlers as handlers_proyeccion
from modulos.seguimiento.infraestructura.dto import EstadoSiniestroDTO
from modulos.siniestros.infraestructura.dto import EventoSiniestroDTO
from modulos.siniestros.infraestructura.mapeadores_eventos import dict_a_evento

# Mismo mapeo tipo de evento -> handler de proyección que registra
# seguimiento.aplicacion.handlers.registrar_handlers().
_APLICADORES = {
    "SiniestroRegistrado": handlers_proyeccion._al_registrar_siniestro,
    "ProveedorAsignado": handlers_proyeccion._al_asignar_proveedor,
    "SiniestroValidado": handlers_proyeccion._al_validar_siniestro,
    "SiniestroRechazado": handlers_proyeccion._al_rechazar_siniestro,
}


@dataclass
class ReconstruirProyeccion(Comando):
    id_siniestro: str | None = None  # None => reconstruye la proyección completa


class ReconstruirProyeccionHandler(ComandoHandler):
    def handle(self, comando: ReconstruirProyeccion) -> dict:
        session = SessionLocal()
        try:
            filas_proyeccion = session.query(EstadoSiniestroDTO)
            eventos = session.query(EventoSiniestroDTO)
            if comando.id_siniestro:
                filas_proyeccion = filas_proyeccion.filter_by(
                    id_siniestro=comando.id_siniestro
                )
                eventos = eventos.filter_by(siniestro_id=comando.id_siniestro)

            # 1. Truncar las filas afectadas de la proyección.
            filas_proyeccion.delete()
            session.commit()

            # 2. Leer los eventos en orden por agregado y versión.
            filas_eventos = eventos.order_by(
                EventoSiniestroDTO.siniestro_id, EventoSiniestroDTO.version
            ).all()
        finally:
            session.close()

        # 3. Reaplicar cada evento contra el handler de proyección.
        aplicados = 0
        for fila in filas_eventos:
            aplicador = _APLICADORES.get(fila.tipo)
            if aplicador is None:
                continue  # tipo sin efecto en esta proyección
            aplicador(dict_a_evento(fila.tipo, fila.datos))
            aplicados += 1
        return {"eventos_reaplicados": aplicados}


@ejecutar_comando.register(ReconstruirProyeccion)
def _(comando: ReconstruirProyeccion):
    return ReconstruirProyeccionHandler().handle(comando)
