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
    DRG_API_PULL_URL: str = "https://api-exportacaoassistencial.iagsaude.com/guiainternacao/search"
    DRG_USERNAME: str = "1_import_guias"
    DRG_PASSWORD: str = "BX!c1tm9sqJp"
    DRG_API_KEY: str = "298d9c85-65af-44f9-b684-0dd92dcb3e57"
    DRG_PULL_USERNAME: str = "1632-I-EXPORTA_GUIA"  # Usuário para PULL
    DRG_PULL_PASSWORD: str = "JOvZeHKqGkr3"  # Senha para PULL
    DRG_PULL_API_KEY: Optional[str] = None  # Opcional: usa DRG_API_KEY se não informado

    # Configurações de log
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # Configurações de anexos
    ANEXOS_BASE_PATH: Optional[str] = None

    # Configurações de segurança
    HTTP_TIMEOUT: int = 120  # Timeout aumentado para 120s (2 minutos) para evitar 504 em lotes grandes
    TOKEN_REFRESH_INTERVAL: float = 3.5

    # Configurações de monitoramento (opcional)
    SENTRY_DSN: Optional[str] = None

    # Configurações de monitoramento automático
    AUTO_MONITOR_ENABLED: bool = True
    MONITOR_INTERVAL_MINUTES: int = 5
    MONITOR_BATCH_SIZE: int = 5  # Tamanho do lote enviado para API DRG (processa TODAS as guias 'A' em lotes deste tamanho)
    MONITOR_PULL_ENABLED: bool = True  # Monitoramento PULL da DRG
    MONITOR_PULL_INTERVAL_MINUTES: int = 5  # Intervalo para buscar retorno
    MONITOR_PULL_MAX_PAGE_SIZE: int = 100  # Máximo de registros por página

    # Configurações para consulta externa de guias
    CONSULTA_EXTERNA_TIMEOUT_MS: int = 30000  # 30 segundos em milissegundos
    CONSULTA_EXTERNA_MAX_TENTATIVAS: int = 3
    CONSULTA_EXTERNA_INTERVALO_MS: int = 60000  # 1 minuto entre tentativas
    CONSULTA_EXTERNA_URL: str = (
        "https://api.externa.com/consultar-guia"  # URL padrão da consulta externa
    )

    # Configurações para monitoramento de campos
    MONITOR_CAMPOS_ENABLED: bool = True
    MONITOR_CAMPOS_INTERVALO_MINUTES: int = 10  # Intervalo entre verificações
    MONITOR_CAMPOS_TIMEOUT_MINUTES: int = (
        30  # Tempo limite para considerar guia atualizada
    )

    # Configurações de rate limiting
    RATE_LIMIT_MONITOR_MINUTES: int = 10
    RATE_LIMIT_CONSULTA_EXTERNA_MINUTES: int = 30
    RATE_LIMIT_CONSULTA_MULTIPLA_MINUTES: int = 10
    RATE_LIMIT_DEFAULT_MINUTES: int = 5

    # Configurações padrão do hospital (valores do .env)
    HOSPITAL_CODIGO_CONTRATADO: str = "5499"
    HOSPITAL_NOME: str = "HOSPITAL I9MED"
    HOSPITAL_CNES: str = "9632587"
    HOSPITAL_PORTE: str = "2"
    HOSPITAL_COMPLEXIDADE: str = "1"
    HOSPITAL_ESFERA_ADMINISTRATIVA: str = "2"
    HOSPITAL_ENDERECO: str = "Endereço não informado"

    # Configurações específicas para PUT DRG
    DRG_PUT_TIMEOUT_MS: int = 30000
    DRG_PUT_MAX_TENTATIVAS: int = 3

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
