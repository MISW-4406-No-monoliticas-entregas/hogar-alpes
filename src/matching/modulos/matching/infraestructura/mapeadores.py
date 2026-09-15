"""Mapeadores entre entidades de dominio y modelos SQLAlchemy."""
import uuid

from modulos.matching.dominio.entidades import Asignacion, ProveedorHabilitado
from modulos.matching.dominio.objetos_valor import Servicio, Zona, EstadoAsignacion
from modulos.matching.infraestructura.dto import AsignacionDTO, ProveedorHabilitadoDTO


class MapeadorAsignacionDTO:
    def entidad_a_dto(self, a: Asignacion) -> AsignacionDTO:
        return AsignacionDTO(
            id=str(a.id),
            id_siniestro=a.id_siniestro,
            servicio=a.servicio.valor,
            zona=a.zona.valor,
            proveedor_id=a.proveedor_id,
            nombre_proveedor=a.nombre_proveedor,
            estado=a.estado.value,
            fecha_creacion=a.fecha_creacion,
            fecha_actualizacion=a.fecha_actualizacion,
        )

    def dto_a_entidad(self, dto: AsignacionDTO) -> Asignacion:
        asignacion = Asignacion(
            id=uuid.UUID(dto.id),
            id_siniestro=dto.id_siniestro,
            servicio=Servicio(dto.servicio),
            zona=Zona(dto.zona),
            proveedor_id=dto.proveedor_id,
            nombre_proveedor=dto.nombre_proveedor,
            estado=EstadoAsignacion(dto.estado),
        )
        asignacion._fecha_creacion = dto.fecha_creacion
        asignacion._fecha_actualizacion = dto.fecha_actualizacion
        return asignacion


class MapeadorProveedorHabilitadoDTO:
    def entidad_a_dto(self, p: ProveedorHabilitado) -> ProveedorHabilitadoDTO:
        return ProveedorHabilitadoDTO(
            id=str(p.id),
            nombre=p.nombre,
            servicio=p.servicio.valor,
            zona=p.zona.valor,
            disponible=p.disponible,
            fecha_creacion=p.fecha_creacion,
            fecha_actualizacion=p.fecha_actualizacion,
        )

    def dto_a_entidad(self, dto: ProveedorHabilitadoDTO) -> ProveedorHabilitado:
        proveedor = ProveedorHabilitado(
            id=uuid.UUID(dto.id),
            nombre=dto.nombre,
            servicio=Servicio(dto.servicio),
            zona=Zona(dto.zona),
            disponible=dto.disponible,
        )
        proveedor._fecha_creacion = dto.fecha_creacion
        proveedor._fecha_actualizacion = dto.fecha_actualizacion
        return proveedor
