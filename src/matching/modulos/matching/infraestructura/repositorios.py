"""Repositorios CRUD con SQLAlchemy (adaptadores de salida)."""
import uuid

from modulos.matching.dominio.repositorios import (
    RepositorioAsignaciones,
    RepositorioProveedoresHabilitados,
)
from modulos.matching.dominio.entidades import Asignacion, ProveedorHabilitado
from modulos.matching.dominio.objetos_valor import EstadoAsignacion
from modulos.matching.infraestructura.dto import AsignacionDTO, ProveedorHabilitadoDTO
from modulos.matching.infraestructura.mapeadores import (
    MapeadorAsignacionDTO,
    MapeadorProveedorHabilitadoDTO,
)


class RepositorioAsignacionesSQLAlchemy(RepositorioAsignaciones):
    def __init__(self, session):
        self.session = session
        self.mapeador = MapeadorAsignacionDTO()

    def obtener_por_id(self, id: uuid.UUID) -> Asignacion | None:
        dto = self.session.get(AsignacionDTO, str(id))
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def obtener_asignada_por_siniestro(self, id_siniestro: str) -> Asignacion | None:
        dto = (
            self.session.query(AsignacionDTO)
            .filter(
                AsignacionDTO.id_siniestro == id_siniestro,
                AsignacionDTO.estado == EstadoAsignacion.ASIGNADA.value,
            )
            .order_by(AsignacionDTO.fecha_creacion.desc())
            .first()
        )
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def agregar(self, asignacion: Asignacion):
        self.session.add(self.mapeador.entidad_a_dto(asignacion))

    def actualizar(self, asignacion: Asignacion):
        self.session.merge(self.mapeador.entidad_a_dto(asignacion))


class RepositorioProveedoresHabilitadosSQLAlchemy(RepositorioProveedoresHabilitados):
    def __init__(self, session):
        self.session = session
        self.mapeador = MapeadorProveedorHabilitadoDTO()

    def obtener_por_id(self, id: uuid.UUID) -> ProveedorHabilitado | None:
        dto = self.session.get(ProveedorHabilitadoDTO, str(id))
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def buscar_disponible(self, servicio: str, zona: str) -> ProveedorHabilitado | None:
        dto = (
            self.session.query(ProveedorHabilitadoDTO)
            .filter(
                ProveedorHabilitadoDTO.servicio == servicio,
                ProveedorHabilitadoDTO.zona == zona,
                ProveedorHabilitadoDTO.disponible.is_(True),
            )
            .order_by(ProveedorHabilitadoDTO.id)
            .first()
        )
        return self.mapeador.dto_a_entidad(dto) if dto else None

    def listar_por_zona_servicio(self, zona: str, servicio: str) -> list[ProveedorHabilitado]:
        filas = (
            self.session.query(ProveedorHabilitadoDTO)
            .filter(
                ProveedorHabilitadoDTO.zona == zona,
                ProveedorHabilitadoDTO.servicio == servicio,
            )
            .order_by(ProveedorHabilitadoDTO.nombre)
            .all()
        )
        return [self.mapeador.dto_a_entidad(dto) for dto in filas]

    def agregar(self, proveedor: ProveedorHabilitado):
        self.session.add(self.mapeador.entidad_a_dto(proveedor))

    def actualizar(self, proveedor: ProveedorHabilitado):
        self.session.merge(self.mapeador.entidad_a_dto(proveedor))
