"""SQLAlchemy sobre PostgreSQL (adaptador de persistencia).

Expone la Base declarativa compartida y una fábrica de sesiones. Los modelos
(DTO SQLAlchemy) de cada módulo heredan de Base; la UoW usa SessionLocal.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)

Base = declarative_base()


def crear_tablas():
    """Crea las tablas si no existen.

    El import de los modelos es diferido para evitar dependencias circulares y
    para registrarlos en la metadata de la Base antes de create_all.
    """
    from modulos.siniestros.infraestructura import dto as _dto_siniestros
    from modulos.seguimiento.infraestructura import dto as _dto_seguimiento

    Base.metadata.create_all(bind=engine)
