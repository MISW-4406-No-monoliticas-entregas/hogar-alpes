"""Entidades del módulo orquestador: agregado Saga (el Saga Log).

ARCHIVO COMPARTIDO con C (a diferencia de aplicacion/comandos/pasos_felices.py
y aplicacion/comandos/compensaciones.py, que sí están separados). Este es el
agregado que persiste en qué paso va cada transacción larga -- ambos caminos
(feliz y de fallo) leen y escriben la misma fila. Avisar antes de tocarlo.

Métodos que trae esta parte (D -- compensación):
  - `iniciar`: arranca la saga (también la usa D si compensar_saga.py no
    encuentra fila, para no perder el registro del fallo).
  - `registrar_proveedor_reservado`: anota qué proveedor confirmó S7, sin
    tocar paso/estado -- así se sabe qué liberar si algo falla después.
  - `compensar` / `completar_compensacion`: el camino de fallo completo.

C probablemente necesite agregar sus propios métodos para el camino feliz
(`avanzar_a_validando`, `avanzar_a_asignando`, `completar`, o los que decida)
sin que choquen con los de arriba.
"""
from dataclasses import dataclass

from seedwork.dominio.entidades import AgregacionRaiz
from modulos.orquestador.dominio.objetos_valor import PasoSaga, EstadoSaga
from modulos.orquestador.dominio.eventos import CompensacionIniciada
from modulos.orquestador.dominio.reglas import (
    ElSiniestroEsObligatorio,
    SoloSePuedeCompensarUnaSagaEnCurso,
)


@dataclass
class Saga(AgregacionRaiz):
    """Fila del Saga Log: en qué paso va la transacción larga de un siniestro."""
    siniestro_id: str = None
    paso_actual: PasoSaga = None
    estado: EstadoSaga = None
    proveedor_id: str | None = None
    motivo_fallo: str | None = None

    def iniciar(self, siniestro_id: str):
        self.validar_regla(ElSiniestroEsObligatorio(siniestro_id))
        self.siniestro_id = siniestro_id
        self.paso_actual = PasoSaga.INICIADA
        self.estado = EstadoSaga.EN_CURSO

    def registrar_proveedor_reservado(self, proveedor_id: str):
        """S7 confirmó una reserva (evento ProveedorAsignado): se anota para
        poder liberarla si un paso posterior de la saga todavía falla. No
        cambia el paso ni el estado -- eso lo decide el camino feliz."""
        self.proveedor_id = proveedor_id
        self._marcar_actualizacion()

    def compensar(self, motivo: str):
        """Camino de fallo: marca COMPENSANDO y emite el evento que dispara
        las compensaciones que correspondan (RechazarSiniestro siempre;
        LiberarProveedor solo si ya había un `proveedor_id` reservado)."""
        self.validar_regla(SoloSePuedeCompensarUnaSagaEnCurso(self.estado))
        self.paso_actual = PasoSaga.COMPENSANDO
        self.estado = EstadoSaga.FALLIDO
        self.motivo_fallo = motivo
        self.agregar_evento(
            CompensacionIniciada(
                id_saga=self.id,
                siniestro_id=self.siniestro_id,
                motivo=motivo,
                proveedor_id=self.proveedor_id,
            )
        )

    def completar_compensacion(self):
        """Cierra el camino de fallo una vez publicadas las compensaciones."""
        self.paso_actual = PasoSaga.COMPENSADA
        self._marcar_actualizacion()
