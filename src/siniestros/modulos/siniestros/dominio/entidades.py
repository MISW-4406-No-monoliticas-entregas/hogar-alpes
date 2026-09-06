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
)
from modulos.siniestros.dominio.reglas import (
    LaPolizaEsObligatoria,
    ElMontoEstimadoDebeSerPositivo,
    ElSiniestroDebeEstarRegistradoParaAsignar,
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

    def agregar_evidencia(self, descripcion: str, url: str):
        self.evidencias.append(Evidencia(descripcion=descripcion, url=url))
        self._marcar_actualizacion()
