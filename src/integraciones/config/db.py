"""SQLAlchemy sobre PostgreSQL. El engine se crea de forma perezosa."""
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
    _inicializar()
    return _session_factory()


def crear_tablas():
    """Crea las tablas si no existen."""
    from modulos.sincronizaciones.infraestructura import dto as _dto  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
