#!/usr/bin/env python3
"""
FastAPI Application para Sistema DRG - Guias de Internação
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import asyncio

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)

# Importar configurações e serviços
from app.config.config import get_settings
from app.database.database import init_db
from app.services.monitor_service import monitor_service
from app.services.monitor_campos_service import monitor_campos_service
from app.services.monitor_pull_service import monitor_pull_service
from app.middleware.security import setup_security_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação FastAPI."""
    # Startup
    logger.info("Iniciando aplicação FastAPI...")

    # Inicializar banco de dados
    init_db()

    # Iniciar monitoramento automático
    await monitor_service.start_monitoring()

    # Iniciar monitoramento de campos se habilitado
    settings = get_settings()
    if settings.MONITOR_CAMPOS_ENABLED:
        logger.info("🚀 Iniciando monitoramento automático de campos...")
        monitor_campos_service._running = True
        monitor_campos_service._task = asyncio.create_task(
            monitor_campos_service.iniciar_monitoramento_continuo()
        )
        logger.info("✅ Monitoramento de campos iniciado")
    else:
        logger.info("🔕 Monitoramento de campos desabilitado")

    # Iniciar monitoramento PULL se habilitado
    await monitor_pull_service.iniciar_monitoramento_pull()

    logger.info("Aplicação FastAPI iniciada com sucesso!")

    yield

    # Shutdown
    logger.info("Encerrando aplicação FastAPI...")

    # Parar monitoramento automático
    await monitor_service.stop_monitoring()

    # Parar monitoramento de campos
    if monitor_campos_service._running:
        logger.info("🛑 Parando monitoramento de campos...")
        monitor_campos_service._running = False
        if monitor_campos_service._task:
            monitor_campos_service._task.cancel()
            try:
                await monitor_campos_service._task
            except asyncio.CancelledError:
                pass
        logger.info("✅ Monitoramento de campos parado")

    # Parar monitoramento PULL
    await monitor_pull_service.parar_monitoramento_pull()


def create_app() -> FastAPI:
    """Factory function para criar a aplicação FastAPI."""

    # Criar aplicação FastAPI
    app = FastAPI(
        title="DRG Guias API",
        description="API para processamento de guias de internação DRG",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configurar rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Configurar middleware de segurança
    setup_security_middleware(app)

    # Configurar CORS (mais restritivo em produção)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Em produção, especificar domínios específicos
        allow_credentials=True,
        allow_methods=["GET", "POST"],  # Apenas métodos necessários
        allow_headers=["*"],
    )

    # Registrar rotas
    from app.routes.fastapi_routes import router

    app.include_router(router, prefix="/api/v1")

    return app


# Criar instância da aplicação
app = create_app()


if __name__ == "__main__":
    import uvicorn

    # Carregar configurações
    settings = get_settings()

    # Executar servidor
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEVELOPMENT,
        log_level="info",
    )
