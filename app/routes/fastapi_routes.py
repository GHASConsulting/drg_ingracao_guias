#!/usr/bin/env python3
"""
Rotas FastAPI para o sistema DRG
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database.database import get_db
from app.models import Guia, Anexo, Procedimento, Diagnostico
from app.schemas.guia_schema import (
    GuiaResponseSchema,
    EntradaSchema,
)
from app.schemas.response_schema import (
    ErrorResponseSchema,
    SuccessResponseSchema,
    SystemStatusResponseSchema,
    ListaGuiasResponseSchema,
)
from app.services.drg_service import DRGService
from app.services.guia_service import GuiaService
from app.services.monitor_service import monitor_service

# Configurar logging
logger = logging.getLogger(__name__)

# Criar router
router = APIRouter()

# Rate limiter para as rotas
limiter = Limiter(key_func=get_remote_address)


@router.get("/health", response_model=dict)
@limiter.limit("100/minute")
async def health_check(request: Request):
    """Verifica saúde da API."""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "service": "DRG API",
        }
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@router.get("/status", response_model=dict)
@limiter.limit("30/minute")
async def system_status(request: Request, db: Session = Depends(get_db)):
    """Retorna status do sistema."""
    try:
        # Contar guias por status
        total_guias = db.query(Guia).count()
        aguardando = db.query(Guia).filter(Guia.tp_status == "A").count()
        transmitidas = db.query(Guia).filter(Guia.tp_status == "T").count()
        com_erro = db.query(Guia).filter(Guia.tp_status == "E").count()

        # Status do DRG
        drg_service = DRGService()
        drg_status = drg_service.get_token_status()

        return {
            "sistema": {
                "status": "operacional",
                "timestamp": datetime.utcnow().isoformat(),
            },
            "guias": {
                "total": total_guias,
                "aguardando": aguardando,
                "transmitidas": transmitidas,
                "com_erro": com_erro,
            },
            "drg_api": {
                "status": "conectado" if drg_status["sucesso"] else "erro",
                "token_valido": drg_status.get("token_info", {}).get(
                    "has_token", False
                ),
            },
        }

    except Exception as e:
        logger.error(f"Erro no status do sistema: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "sistema": {
                    "status": "erro",
                    "erro": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            },
        )


@router.get("/guias", response_model=List[GuiaResponseSchema])
@limiter.limit("60/minute")
async def listar_guias(
    request: Request,
    status: Optional[str] = Query(None, description="Filtrar por status"),
    limit: int = Query(50, ge=1, le=100, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginação"),
    db: Session = Depends(get_db),
):
    """Lista todas as guias com filtros opcionais."""
    try:
        # Query base
        query = db.query(Guia)

        # Aplicar filtros
        if status:
            query = query.filter(Guia.tp_status == status.upper())

        # Paginação
        query = query.offset(offset).limit(limit)

        # Executar query
        guias = query.all()

        return guias

    except Exception as e:
        logger.error(f"Erro ao listar guias: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/guias/{guia_id}", response_model=dict)
async def consultar_guia(
    guia_id: int = Path(..., description="ID da guia"), db: Session = Depends(get_db)
):
    """Consulta uma guia específica com todos os dados."""
    try:
        # Buscar guia
        guia = db.query(Guia).filter(Guia.id == guia_id).first()

        if not guia:
            raise HTTPException(status_code=404, detail="Guia não encontrada")

        # Buscar relacionamentos
        anexos = db.query(Anexo).filter(Anexo.guia_id == guia_id).all()
        procedimentos = (
            db.query(Procedimento).filter(Procedimento.guia_id == guia_id).all()
        )
        diagnosticos = (
            db.query(Diagnostico).filter(Diagnostico.guia_id == guia_id).all()
        )

        # Montar resposta completa
        result = {
            "guia": GuiaResponseSchema.from_orm(guia).dict(),
            "anexos": [
                {"id": a.id, "nome": a.nome, "tipo_documento": a.tipo_documento}
                for a in anexos
            ],
            "procedimentos": [
                {
                    "id": p.id,
                    "codigo": p.codigo,
                    "descricao": p.descricao,
                    "valor_unitario": float(p.valor_unitario),
                }
                for p in procedimentos
            ],
            "diagnosticos": [
                {"id": d.id, "codigo": d.codigo, "tipo": d.tipo} for d in diagnosticos
            ],
        }

        return {"success": True, "data": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao consultar guia {guia_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/guias/{guia_id}/processar", response_model=dict)
async def processar_guia(
    guia_id: int = Path(..., description="ID da guia"), db: Session = Depends(get_db)
):
    """Processa uma guia específica."""
    try:
        # Buscar guia
        guia = db.query(Guia).filter(Guia.id == guia_id).first()

        if not guia:
            raise HTTPException(status_code=404, detail="Guia não encontrada")

        if guia.tp_status not in ["A", "E"]:
            raise HTTPException(
                status_code=400,
                detail=f"Guia não pode ser processada (status: {guia.tp_status})",
            )

        # Verificar tentativas
        if guia.tentativas >= 2:
            raise HTTPException(status_code=400, detail="Máximo de tentativas excedido")

        # Atualizar status para processando
        guia.tp_status = "P"  # Processando
        guia.tentativas += 1
        guia.data_processamento = datetime.utcnow()

        db.commit()

        # Montar JSON para DRG
        guia_service = GuiaService()
        json_drg = guia_service.montar_json_drg(guia)

        # Enviar para DRG
        drg_service = DRGService()
        resultado = drg_service.enviar_guia(json_drg)

        if resultado["sucesso"]:
            # Sucesso
            guia.tp_status = "T"  # Transmitida
            guia.mensagem_erro = None
        else:
            # Erro
            guia.tp_status = "E"  # Erro
            guia.mensagem_erro = resultado["erro"]

        db.commit()

        return {
            "success": resultado["sucesso"],
            "data": {
                "guia_id": guia_id,
                "status": guia.tp_status,
                "tentativas": guia.tentativas,
                "mensagem": resultado.get("mensagem", guia.mensagem_erro),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar guia {guia_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/guias/{guia_id}/reprocessar", response_model=dict)
async def reprocessar_guia(
    guia_id: int = Path(..., description="ID da guia"), db: Session = Depends(get_db)
):
    """Reprocessa uma guia com erro."""
    try:
        # Buscar guia
        guia = db.query(Guia).filter(Guia.id == guia_id).first()

        if not guia:
            raise HTTPException(status_code=404, detail="Guia não encontrada")

        if guia.tp_status != "E":
            raise HTTPException(
                status_code=400, detail="Apenas guias com erro podem ser reprocessadas"
            )

        # Resetar para aguardando
        guia.tp_status = "A"
        guia.mensagem_erro = None
        guia.tentativas = 0

        db.commit()

        return {
            "success": True,
            "data": {
                "guia_id": guia_id,
                "status": "A",
                "mensagem": "Guia resetada para reprocessamento",
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao reprocessar guia {guia_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drg/token", response_model=dict)
async def status_token():
    """Retorna status do token DRG."""
    try:
        drg_service = DRGService()
        resultado = drg_service.get_token_status()

        return {
            "success": resultado["sucesso"],
            "data": resultado.get("token_info", {}),
            "error": resultado.get("erro"),
        }

    except Exception as e:
        logger.error(f"Erro ao consultar token DRG: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/drg/token/renovar", response_model=dict)
async def renovar_token():
    """Renova o token DRG."""
    try:
        drg_service = DRGService()
        resultado = drg_service.renovar_token()

        return {
            "success": resultado["sucesso"],
            "data": {
                "token": (
                    resultado.get("token", "")[:50] + "..."
                    if resultado.get("token")
                    else None
                ),
                "renovado_em": datetime.utcnow().isoformat(),
            },
            "error": resultado.get("erro"),
        }

    except Exception as e:
        logger.error(f"Erro ao renovar token DRG: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoramento", response_model=dict)
async def monitoramento(db: Session = Depends(get_db)):
    """Retorna informações de monitoramento do sistema."""
    try:
        # Estatísticas gerais
        total_guias = db.query(Guia).count()
        aguardando = db.query(Guia).filter(Guia.tp_status == "A").count()
        processando = db.query(Guia).filter(Guia.tp_status == "P").count()
        transmitidas = db.query(Guia).filter(Guia.tp_status == "T").count()
        com_erro = db.query(Guia).filter(Guia.tp_status == "E").count()

        # Guias com erro recente
        guias_erro = (
            db.query(Guia)
            .filter(Guia.tp_status == "E", Guia.tentativas >= 2)
            .limit(10)
            .all()
        )

        # Status DRG
        drg_service = DRGService()
        drg_status = drg_service.get_token_status()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "estatisticas": {
                "total_guias": total_guias,
                "aguardando": aguardando,
                "processando": processando,
                "transmitidas": transmitidas,
                "com_erro": com_erro,
                "taxa_sucesso": (
                    round((transmitidas / total_guias * 100), 2)
                    if total_guias > 0
                    else 0
                ),
            },
            "guias_com_erro": [
                {
                    "id": g.id,
                    "numero_guia": g.numero_guia,
                    "tentativas": g.tentativas,
                    "mensagem_erro": g.mensagem_erro,
                }
                for g in guias_erro
            ],
            "drg_api": {
                "status": "conectado" if drg_status["sucesso"] else "erro",
                "token_valido": drg_status.get("token_info", {}).get(
                    "has_token", False
                ),
            },
        }

    except Exception as e:
        logger.error(f"Erro no monitoramento: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "timestamp": datetime.utcnow().isoformat()},
        )


# =============================================================================
# ROTAS DE MONITORAMENTO AUTOMÁTICO
# =============================================================================


@router.get("/monitoramento/status", response_model=dict)
async def get_monitoring_status():
    """
    Retorna o status do monitoramento automático da tabela.
    """
    try:
        status = await monitor_service.get_monitoring_status()
        return {
            "success": True,
            "data": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Erro ao obter status do monitoramento: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "timestamp": datetime.utcnow().isoformat()},
        )


@router.post("/monitoramento/start")
async def start_monitoring():
    """
    Inicia o monitoramento automático da tabela.
    """
    try:
        await monitor_service.start_monitoring()
        return {
            "success": True,
            "message": "Monitoramento iniciado com sucesso",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Erro ao iniciar monitoramento: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "timestamp": datetime.utcnow().isoformat()},
        )


@router.post("/monitoramento/stop")
async def stop_monitoring():
    """
    Para o monitoramento automático da tabela.
    """
    try:
        await monitor_service.stop_monitoring()
        return {
            "success": True,
            "message": "Monitoramento parado com sucesso",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Erro ao parar monitoramento: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "timestamp": datetime.utcnow().isoformat()},
        )


# Error handlers serão configurados no main.py
