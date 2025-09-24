from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação usando Pydantic Settings"""

    # Configurações da aplicação
    APP_NAME: str = "DRG Guias API"
    VERSION: str = "1.0.0"
    DEVELOPMENT: bool = True
    TESTING: bool = False

    # Configurações de produção
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Configurações do banco de dados
    DATABASE_TYPE: str = "sqlite"
    DATABASE_URL: str = "sqlite:///database/teste_drg.db"

    # Configurações Oracle
    ORACLE_HOST: str = "localhost"
    ORACLE_PORT: int = 1521
    ORACLE_SID: str = "XE"
    ORACLE_USERNAME: str = "drg_user"
    ORACLE_PASSWORD: str = "drg_password"
    ORACLE_DIR: str = "/opt/oracle/instantclient_21_17"

    # Configurações do Redis (Removido - não necessário)
    # REDIS_URL: str = "redis://localhost:6379/0"

    # Configurações do Celery (Removido - não necessário)
    # CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    # CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Configurações da API DRG
    AUTH_API_URL: str = "https://api-autenticacao.iagsaude.com/login"
    DRG_API_URL: str = "https://api-hospitalar.iagsaude.com/integracao/guias/save"
    DRG_USERNAME: str = "1_import_guias"
    DRG_PASSWORD: str = "BX!c1tm9sqJp"
    DRG_API_KEY: str = "298d9c85-65af-44f9-b684-0dd92dcb3e57"

    # Configurações de log
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # Configurações de segurança
    HTTP_TIMEOUT: int = 60
    TOKEN_REFRESH_INTERVAL: float = 3.5

    # Configurações de monitoramento (opcional)
    SENTRY_DSN: Optional[str] = None

    # Configurações de monitoramento automático
    AUTO_MONITOR_ENABLED: bool = True
    MONITOR_INTERVAL_MINUTES: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignorar variáveis extras


# Instância global das configurações
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Retorna a instância das configurações (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Manter compatibilidade com código antigo
def get_config():
    """Função de compatibilidade para código antigo"""
    return get_settings()


# Configurações por ambiente (para compatibilidade)
class DevelopmentConfig:
    """Configuração de desenvolvimento"""

    DEBUG = True
    TESTING = False


class ProductionConfig:
    """Configuração de produção"""

    DEBUG = False
    TESTING = False


class TestingConfig:
    """Configuração de teste"""

    DEBUG = True
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
