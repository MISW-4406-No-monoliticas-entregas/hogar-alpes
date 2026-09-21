"""Entidades del modulo orquestador: agregado Saga (el Saga Log).

ARCHIVO COMPARTIDO entre C y D (a diferencia de aplicacion/comandos/
pasos_felices.py y aplicacion/comandos/compensaciones.py, que si estan
separados). Este es el agregado que persiste en que paso va cada transaccion
larga: ambos caminos leen y escriben la misma fila.

Camino feliz (C):
  - `iniciar_pendiente`: crea la saga cuando todavia no hay id_siniestro,
    guardando partner/poliza (correlacion) y servicio/zona (datos que ningun
    evento de S2 transporta).
  - `vincular_siniestro`: S2 aviso el id, la saga pasa a INICIADA.
  - `avanzar_a_validando` / `avanzar_a_asignando` / `completar`: los tres
    avances del camino feliz, cada uno emite el evento que dispara el comando
    hacia el servicio que sigue.

Camino de fallo (D):
  - `registrar_proveedor_reservado`, `compensar`, `completar_compensacion`.

Ningun metodo del camino feliz toca los de D: la unica regla compartida es que
los dos se apoyan en `paso_actual` y `estado`.
"""
from dataclasses import dataclass

from seedwork.dominio.entidades import AgregacionRaiz
from modulos.orquestador.dominio.objetos_valor import PasoSaga, EstadoSaga
from modulos.orquestador.dominio.eventos import (
    CompensacionIniciada,
    RegistroRequerido,
    ValidacionRequerida,
    AsignacionRequerida,
    SagaCompletada,
)
from modulos.orquestador.dominio.reglas import (
    ElSiniestroEsObligatorio,
    SoloSePuedeCompensarUnaSagaEnCurso,
    ElPartnerYLaPolizaSonObligatorios,
    LaSagaDebeEstarEnElPasoEsperado,
)


@dataclass
class Saga(AgregacionRaiz):
    """Fila del Saga Log: en que paso va la transaccion larga de un siniestro."""
    siniestro_id: str = None
    paso_actual: PasoSaga = None
    estado: EstadoSaga = None
    proveedor_id: str | None = None
    motivo_fallo: str | None = None
    partner_id: str | None = None
    poliza: str | None = None
    servicio: str | None = None
    zona: str | None = None

    def iniciar(self, siniestro_id: str):
        self.validar_regla(ElSiniestroEsObligatorio(siniestro_id))
        self.siniestro_id = siniestro_id
        self.paso_actual = PasoSaga.INICIADA
        self.estado = EstadoSaga.EN_CURSO

    def iniciar_pendiente(self, partner_id: str, poliza: str, servicio: str, zona: str,
                          monto: float, moneda: str, calle: str, ciudad: str, pais: str):
        """Arranca la saga antes de que exista el siniestro.

        S2 es quien genera el id_siniestro, asi que la saga nace sin el y se
        correlaciona despues por (partner_id, poliza). servicio y zona se
        guardan aqui porque no viajan en ningun evento de S2 y el paso de
        validacion los necesita.
        """
        self.validar_regla(ElPartnerYLaPolizaSonObligatorios(partner_id, poliza))
        self.partner_id = partner_id
        self.poliza = poliza
        self.servicio = servicio
        self.zona = zona
        self.paso_actual = PasoSaga.PENDIENTE
        self.estado = EstadoSaga.EN_CURSO
        self.agregar_evento(
            RegistroRequerido(
                id_saga=self.id,
                partner_id=partner_id,
                poliza=poliza,
                monto=monto,
                moneda=moneda,
                calle=calle,
                ciudad=ciudad,
                pais=pais,
            )
        )

    def vincular_siniestro(self, siniestro_id: str):
        """S2 registro el siniestro: la saga ya tiene a que agregado apuntar."""
        self.validar_regla(
            LaSagaDebeEstarEnElPasoEsperado(self.paso_actual, (PasoSaga.PENDIENTE,))
        )
        self.validar_regla(ElSiniestroEsObligatorio(siniestro_id))
        self.siniestro_id = siniestro_id
        self.paso_actual = PasoSaga.INICIADA
        self._marcar_actualizacion()

    def avanzar_a_validando(self, monto: float, moneda: str):
        """Pide a S10 que evalue las reglas del partner."""
        self.validar_regla(
            LaSagaDebeEstarEnElPasoEsperado(self.paso_actual, (PasoSaga.INICIADA,))
        )
        self.paso_actual = PasoSaga.VALIDANDO
        self._marcar_actualizacion()
        self.agregar_evento(
            ValidacionRequerida(
                id_saga=self.id,
                siniestro_id=self.siniestro_id,
                partner_id=self.partner_id,
                monto=monto,
                moneda=moneda,
                servicio=self.servicio,
                zona=self.zona,
            )
        )

    def avanzar_a_asignando(self, servicio: str = None, zona: str = None):
        """Las reglas aprobaron: pide a S7 un proveedor habilitado."""
        self.validar_regla(
            LaSagaDebeEstarEnElPasoEsperado(self.paso_actual, (PasoSaga.VALIDANDO,))
        )
        if servicio:
            self.servicio = servicio
        if zona:
            self.zona = zona
        self.paso_actual = PasoSaga.ASIGNANDO
        self._marcar_actualizacion()
        self.agregar_evento(
            AsignacionRequerida(
                id_saga=self.id,
                siniestro_id=self.siniestro_id,
                servicio=self.servicio,
                zona=self.zona,
            )
        )

    def completar(self):
        """S7 reservo proveedor: la transaccion larga cerro bien."""
        self.validar_regla(
            LaSagaDebeEstarEnElPasoEsperado(self.paso_actual, (PasoSaga.ASIGNANDO,))
        )
        self.paso_actual = PasoSaga.COMPLETADA
        self.estado = EstadoSaga.OK
        self._marcar_actualizacion()
        self.agregar_evento(
            SagaCompletada(
                id_saga=self.id,
                siniestro_id=self.siniestro_id,
                proveedor_id=self.proveedor_id,
            )
        )

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
