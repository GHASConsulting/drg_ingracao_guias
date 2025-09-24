"""
Configuração do banco de dados para FastAPI
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.config.config import get_settings
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Base para modelos
Base = declarative_base()

# Variáveis globais para engine e session
engine = None
SessionLocal = None


def init_db():
    """Inicializa o banco de dados"""
    global engine, SessionLocal

    settings = get_settings()

    # Configurar engine baseado no tipo de banco
    if settings.DATABASE_TYPE == "sqlite":
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=settings.DEVELOPMENT,
        )
    else:
        engine = create_engine(settings.DATABASE_URL, echo=settings.DEVELOPMENT)

    # Criar session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Criar tabelas se não existirem
    Base.metadata.create_all(bind=engine)

    logger.info(f"Banco de dados inicializado: {settings.DATABASE_TYPE}")


def get_db() -> Generator[Session, None, None]:
    """Dependency para obter sessão do banco de dados"""
    if SessionLocal is None:
        init_db()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Compatibilidade com código antigo
def get_session() -> Session:
    """Retorna uma sessão do banco de dados (para uso direto)"""
    if SessionLocal is None:
        init_db()
    return SessionLocal()


# Para compatibilidade com Flask-SQLAlchemy
class Database:
    """Classe de compatibilidade para Flask-SQLAlchemy"""

    def __init__(self):
        self.session = None

    def init_app(self, app):
        """Método de compatibilidade"""
        pass


# Instância para compatibilidade
db = Database()
