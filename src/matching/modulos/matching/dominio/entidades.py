"""Entidades del módulo matching: agregado Asignacion y el modelo de lectura
ProveedorHabilitado.

`ProveedorHabilitado` no es una agregación raíz: es el modelo de lectura/config
que alimenta el matching (una fila por proveedor+servicio+zona). No emite
eventos de dominio; su disponibilidad se muta como efecto colateral de manejar
comandos sobre el agregado `Asignacion`.
"""
from dataclasses import dataclass

from seedwork.dominio.entidades import Entidad, AgregacionRaiz
from modulos.matching.dominio.objetos_valor import Servicio, Zona, EstadoAsignacion
from modulos.matching.dominio.eventos import ProveedorAsignado, SinProveedorDisponible
from modulos.matching.dominio.reglas import (
    ElSiniestroEsObligatorio,
    LaAsignacionDebeEstarAsignadaParaLiberar,
)


@dataclass
class ProveedorHabilitado(Entidad):
    """Proveedor acreditado para un servicio en una zona (lectura/config)."""
    nombre: str = ""
    servicio: Servicio = None
    zona: Zona = None
    disponible: bool = True

    def marcar_ocupado(self):
        self.disponible = False
        self._marcar_actualizacion()

    def marcar_disponible(self):
        self.disponible = True
        self._marcar_actualizacion()


@dataclass
class Asignacion(AgregacionRaiz):
    """Agregado raíz: la reserva de un proveedor para un siniestro."""
    id_siniestro: str = None
    servicio: Servicio = None
    zona: Zona = None
    proveedor_id: str | None = None
    nombre_proveedor: str | None = None
    estado: EstadoAsignacion = None

    def asignar(self, proveedor: ProveedorHabilitado):
        """Reserva `proveedor` para el siniestro y emite ProveedorAsignado."""
        self.validar_regla(ElSiniestroEsObligatorio(self.id_siniestro))
        self.proveedor_id = str(proveedor.id)
        self.nombre_proveedor = proveedor.nombre
        self.estado = EstadoAsignacion.ASIGNADA
        self.agregar_evento(
            ProveedorAsignado(
                id_asignacion=self.id,
                id_siniestro=self.id_siniestro,
                proveedor_id=self.proveedor_id,
                nombre_proveedor=self.nombre_proveedor,
                servicio=self.servicio.valor,
                zona=self.zona.valor,
                estado=self.estado.value,
            )
        )

    def marcar_sin_proveedor(self):
        """No hay proveedor disponible: emite SinProveedorDisponible."""
        self.validar_regla(ElSiniestroEsObligatorio(self.id_siniestro))
        self.estado = EstadoAsignacion.SIN_PROVEEDOR
        self.agregar_evento(
            SinProveedorDisponible(
                id_asignacion=self.id,
                id_siniestro=self.id_siniestro,
                servicio=self.servicio.valor,
                zona=self.zona.valor,
                estado=self.estado.value,
            )
        )

    def liberar(self):
        """Compensación: libera la asignación (sin evento de integración aún)."""
        self.validar_regla(LaAsignacionDebeEstarAsignadaParaLiberar(self.estado))
        self.estado = EstadoAsignacion.LIBERADA
        self._marcar_actualizacion()
