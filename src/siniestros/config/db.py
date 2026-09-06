"""SQLAlchemy sobre PostgreSQL (adaptador de persistencia).

Expone la Base declarativa compartida y una fábrica de sesiones. Los modelos
(DTO SQLAlchemy) de cada módulo heredan de Base; la UoW usa SessionLocal.

El engine se crea de forma perezosa (lazy): SQLAlchemy resuelve el driver de la
base al construir el engine, así que diferir su creación permite importar esta
capa sin exigir el driver hasta que realmente se abre una sesión. La aplicación
usa siempre PostgreSQL; las pruebas de dominio no tocan la base.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import DATABASE_URL

Base = declarative_base()

_engine = None
_session_factory = None


def _inicializar():
    global _engine, _session_factory
    if _engine is None:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
        _session_factory = sessionmaker(
            bind=_engine, expire_on_commit=False, future=True
        )


def get_engine():
    _inicializar()
    return _engine


def SessionLocal():
    """Fábrica de sesiones: crea el engine en el primer uso y devuelve una sesión."""
    _inicializar()
    return _session_factory()


def crear_tablas():
    """Crea las tablas si no existen.

    El import de los modelos es diferido para evitar dependencias circulares y
    para registrarlos en la metadata de la Base antes de create_all.
    """
    from modulos.siniestros.infraestructura import dto as _dto_siniestros
    from modulos.seguimiento.infraestructura import dto as _dto_seguimiento

    Base.metadata.create_all(bind=get_engine())
