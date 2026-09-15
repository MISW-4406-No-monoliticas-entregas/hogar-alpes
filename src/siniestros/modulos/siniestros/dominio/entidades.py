"""Entidades del módulo siniestros: agregado Siniestro y entidades hijas."""
import uuid
from dataclasses import dataclass, field

from seedwork.dominio.entidades import Entidad, AgregacionRaiz
from modulos.siniestros.dominio.objetos_valor import (
    PartnerId,
    Poliza,
    Monto,
    Direccion,
    EstadoSiniestro,
)
from modulos.siniestros.dominio.eventos import (
    SiniestroRegistrado,
    ProveedorAsignado,
    SiniestroValidado,
    SiniestroRechazado,
)
from modulos.siniestros.dominio.reglas import (
    LaPolizaEsObligatoria,
    ElMontoEstimadoDebeSerPositivo,
    ElSiniestroDebeEstarRegistradoParaAsignar,
    ElSiniestroDebeEstarAsignadoParaValidar,
    ElSiniestroNoDebeEstarCerradoParaRechazar,
)


@dataclass
class Evidencia(Entidad):
    """Entidad hija del agregado Siniestro."""
    descripcion: str = ""
    url: str = ""


@dataclass
class Actividad(Entidad):
    """Entidad hija del agregado Siniestro."""
    descripcion: str = ""


@dataclass
class Siniestro(AgregacionRaiz):
    """Agregado raíz del siniestro."""
    partner_id: PartnerId = None
    poliza: Poliza = None
    monto: Monto = None
    direccion: Direccion = None
    estado: EstadoSiniestro = None
    proveedor_id: str | None = None
    motivo_rechazo: str | None = None
    evidencias: list[Evidencia] = field(default_factory=list)
    actividades: list[Actividad] = field(default_factory=list)

    def registrar(self):
        """Valida las reglas de registro y emite SiniestroRegistrado."""
        self.validar_regla(LaPolizaEsObligatoria(self.poliza))
        self.validar_regla(ElMontoEstimadoDebeSerPositivo(self.monto))

        self.estado = EstadoSiniestro.REGISTRADO
        self.actividades.append(Actividad(descripcion="Siniestro registrado"))
        self.agregar_evento(
            SiniestroRegistrado(
                id_siniestro=self.id,
                partner_id=self.partner_id.valor,
                poliza=self.poliza.numero,
                monto=self.monto.valor,
                moneda=self.monto.moneda,
                estado=self.estado.value,
                calle=self.direccion.calle if self.direccion else "",
                ciudad=self.direccion.ciudad if self.direccion else "",
                pais=self.direccion.pais if self.direccion else "CO",
            )
        )

    def asignar_proveedor(self, proveedor_id: str):
        """Asigna un proveedor y emite ProveedorAsignado."""
        self.validar_regla(ElSiniestroDebeEstarRegistradoParaAsignar(self.estado))

        self.proveedor_id = proveedor_id
        self.estado = EstadoSiniestro.ASIGNADO
        self._marcar_actualizacion()
        self.actividades.append(
            Actividad(descripcion=f"Proveedor {proveedor_id} asignado")
        )
        self.agregar_evento(
            ProveedorAsignado(
                id_siniestro=self.id,
                proveedor_id=proveedor_id,
                estado=self.estado.value,
            )
        )

    def marcar_validado(self):
        """Valida las reglas y emite SiniestroValidado."""
        self.validar_regla(ElSiniestroDebeEstarAsignadoParaValidar(self.estado))

        self.estado = EstadoSiniestro.VALIDADO
        self._marcar_actualizacion()
        self.actividades.append(Actividad(descripcion="Siniestro validado"))
        self.agregar_evento(
            SiniestroValidado(id_siniestro=self.id, estado=self.estado.value)
        )

    def rechazar(self, motivo: str):
        """Rechaza el siniestro y emite SiniestroRechazado."""
        self.validar_regla(ElSiniestroNoDebeEstarCerradoParaRechazar(self.estado))

        self.motivo_rechazo = motivo
        self.estado = EstadoSiniestro.RECHAZADO
        self._marcar_actualizacion()
        self.actividades.append(Actividad(descripcion=f"Siniestro rechazado: {motivo}"))
        self.agregar_evento(
            SiniestroRechazado(
                id_siniestro=self.id, motivo=motivo, estado=self.estado.value
            )
        )

    def agregar_evidencia(self, descripcion: str, url: str):
        self.evidencias.append(Evidencia(descripcion=descripcion, url=url))
        self._marcar_actualizacion()

    # ------------------------------------------------------------------
    # Event sourcing: replay. `aplicar` reproduce sobre el estado el efecto
    # de un evento YA validado en su momento; no vuelve a correr reglas de
    # negocio ni emite eventos nuevos.
    # ------------------------------------------------------------------
    def aplicar(self, evento):
        tipo = type(evento).__name__
        aplicador = self._APLICADORES.get(tipo)
        if aplicador is None:
            raise ValueError(f"El agregado Siniestro no sabe aplicar '{tipo}'")
        aplicador(self, evento)

    def _aplicar_registrado(self, evento: SiniestroRegistrado):
        self.partner_id = PartnerId(evento.partner_id)
        self.poliza = Poliza(evento.poliza)
        self.monto = Monto(evento.monto, evento.moneda or "COP")
        self.direccion = Direccion(evento.calle, evento.ciudad, evento.pais or "CO")
        self.estado = EstadoSiniestro.REGISTRADO
        self.actividades.append(Actividad(descripcion="Siniestro registrado"))

    def _aplicar_proveedor_asignado(self, evento: ProveedorAsignado):
        self.proveedor_id = evento.proveedor_id
        self.estado = EstadoSiniestro.ASIGNADO
        self.actividades.append(
            Actividad(descripcion=f"Proveedor {evento.proveedor_id} asignado")
        )

    def _aplicar_validado(self, evento: SiniestroValidado):
        self.estado = EstadoSiniestro.VALIDADO
        self.actividades.append(Actividad(descripcion="Siniestro validado"))

    def _aplicar_rechazado(self, evento: SiniestroRechazado):
        self.motivo_rechazo = evento.motivo
        self.estado = EstadoSiniestro.RECHAZADO
        self.actividades.append(
            Actividad(descripcion=f"Siniestro rechazado: {evento.motivo}")
        )

    _APLICADORES = {
        "SiniestroRegistrado": _aplicar_registrado,
        "ProveedorAsignado": _aplicar_proveedor_asignado,
        "SiniestroValidado": _aplicar_validado,
        "SiniestroRechazado": _aplicar_rechazado,
    }
