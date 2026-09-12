"""Mapeador entre el agregado Ejemplo y su modelo SQLAlchemy."""
import uuid

from modulos.ejemplo.dominio.entidades import Ejemplo
from modulos.ejemplo.dominio.objetos_valor import Nombre, EstadoEjemplo
from modulos.ejemplo.infraestructura.dto import EjemploDTO


class MapeadorEjemploDTO:
    def entidad_a_dto(self, e: Ejemplo) -> EjemploDTO:
        return EjemploDTO(
            id=str(e.id),
            nombre=e.nombre.valor,
            estado=e.estado.value,
            fecha_creacion=e.fecha_creacion,
            fecha_actualizacion=e.fecha_actualizacion,
        )

    def dto_a_entidad(self, dto: EjemploDTO) -> Ejemplo:
        ejemplo = Ejemplo(
            id=uuid.UUID(dto.id),
            nombre=Nombre(dto.nombre),
            estado=EstadoEjemplo(dto.estado),
        )
        ejemplo._fecha_creacion = dto.fecha_creacion
        ejemplo._fecha_actualizacion = dto.fecha_actualizacion
        return ejemplo
