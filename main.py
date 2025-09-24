#!/usr/bin/env python3
"""
FastAPI Application para Sistema DRG - Guias de Internação
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar configurações e serviços
from app.config.config import get_settings
from app.database.database import init_db
from app.services.monitor_service import monitor_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação FastAPI."""
    # Startup
    logger.info("Iniciando aplicação FastAPI...")

    # Inicializar banco de dados
    init_db()

    # Iniciar monitoramento automático
    await monitor_service.start_monitoring()

    logger.info("Aplicação FastAPI iniciada com sucesso!")

    yield

    # Shutdown
    logger.info("Encerrando aplicação FastAPI...")

    # Parar monitoramento automático
    await monitor_service.stop_monitoring()


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

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Em produção, especificar domínios
        allow_credentials=True,
        allow_methods=["*"],
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
