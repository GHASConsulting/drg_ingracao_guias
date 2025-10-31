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
from app.schemas.consulta_externa_schema import (
    ConsultaExternaRequestSchema,
    ConsultaExternaResponseSchema,
    ConsultaMultiplaRequestSchema,
    ConsultaMultiplaResponseSchema,
    StatusConsultaSchema,
)
from app.services.drg_service import DRGService
from app.services.guia_service import GuiaService
from app.services.monitor_service import monitor_service
from app.services.consulta_externa_service import ConsultaExternaService
from app.services.monitor_campos_service import MonitorCamposService
from app.config.config import get_settings

# Configurar logging
logger = logging.getLogger(__name__)

# Criar router
router = APIRouter()

# Rate limiter para as rotas
limiter = Limiter(key_func=get_remote_address)


@router.get("/health", response_model=dict)
@limiter.limit(f"{get_settings().RATE_LIMIT_DEFAULT_MINUTES * 20}/minute")
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
@limiter.limit(f"{get_settings().RATE_LIMIT_DEFAULT_MINUTES * 6}/minute")
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
@limiter.limit(f"{get_settings().RATE_LIMIT_DEFAULT_MINUTES * 12}/minute")
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
            # Erro - verificar se é retentável
            erro_msg = resultado.get("erro", "Erro desconhecido")
            retentavel = resultado.get("retentavel", False)

            if retentavel:
                # Erro retentável (500, timeout, conexão) - manter status 'A' para reenvio
                guia.tp_status = "A"  # Voltar para Aguardando
                guia.mensagem_erro = erro_msg
            else:
                # Erro não-retentável (validação) - marcar como erro
                guia.tp_status = "E"  # Erro
                guia.mensagem_erro = erro_msg

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


# =============================================================================
# ROTAS DE CONSULTA EXTERNA DE GUIAS
# =============================================================================


@router.post("/guias/consulta-externa", response_model=ConsultaExternaResponseSchema)
@limiter.limit(f"{get_settings().RATE_LIMIT_CONSULTA_EXTERNA_MINUTES}/minute")
async def consultar_guia_externa(
    request: Request,
    consulta_request: ConsultaExternaRequestSchema,
    db: Session = Depends(get_db),
):
    """
    Consulta uma guia em uma rota externa.

    Esta rota permite consultar o status de uma guia em uma API externa,
    verificando se foi aprovada ou retornada. Os dados são armazenados
    no banco para controle de status.
    """
    try:
        consulta_service = ConsultaExternaService()

        resultado = await consulta_service.consultar_guia_externa(
            db=db,
            numero_guia=consulta_request.numero_guia,
            data_ultima_atualizacao=consulta_request.data_ultima_atualizacao,
        )

        return ConsultaExternaResponseSchema(
            sucesso=resultado["sucesso"],
            mensagem=resultado.get("mensagem"),
            dados=resultado.get("dados"),
            status_consulta=resultado.get("status_consulta", "P"),
            numero_guia=consulta_request.numero_guia,
        )

    except Exception as e:
        logger.error(
            f"Erro na consulta externa da guia {consulta_request.numero_guia}: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "sucesso": False,
                "erro": f"Erro interno: {str(e)}",
                "numero_guia": consulta_request.numero_guia,
            },
        )


@router.post(
    "/guias/consulta-externa/multipla", response_model=ConsultaMultiplaResponseSchema
)
@limiter.limit(f"{get_settings().RATE_LIMIT_CONSULTA_MULTIPLA_MINUTES}/minute")
async def consultar_multiplas_guias_externas(
    request: Request,
    consulta_request: ConsultaMultiplaRequestSchema,
    db: Session = Depends(get_db),
):
    """
    Consulta múltiplas guias em uma rota externa.

    Esta rota permite consultar o status de várias guias em lote,
    útil para processar grandes volumes de consultas.
    """
    try:
        consulta_service = ConsultaExternaService()

        resultado = await consulta_service.consultar_multiplas_guias(
            db=db,
            guias=consulta_request.guias,
        )

        return ConsultaMultiplaResponseSchema(
            sucesso=resultado["sucesso"],
            total_processadas=resultado["total_processadas"],
            sucessos=resultado["sucessos"],
            erros=resultado["erros"],
            resultados=resultado["resultados"],
        )

    except Exception as e:
        logger.error(f"Erro na consulta múltipla externa: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "sucesso": False,
                "erro": f"Erro interno: {str(e)}",
                "total_processadas": 0,
                "sucessos": 0,
                "erros": len(consulta_request.guias),
            },
        )


@router.get("/guias/{numero_guia}/status-consulta", response_model=StatusConsultaSchema)
async def obter_status_consulta(
    numero_guia: str = Path(..., description="Número da guia"),
    db: Session = Depends(get_db),
):
    """
    Obtém o status de consulta externa de uma guia específica.

    Retorna informações sobre quando foi feita a última consulta,
    qual URL foi consultada e os dados retornados.
    """
    try:
        guia = db.query(Guia).filter(Guia.numero_guia == numero_guia).first()

        if not guia:
            raise HTTPException(
                status_code=404, detail=f"Guia {numero_guia} não encontrada"
            )

        # Parse dos dados retornados se existirem
        dados_retornados = None
        if guia.dados_retornados:
            try:
                import json

                dados_retornados = json.loads(guia.dados_retornados)
            except json.JSONDecodeError:
                dados_retornados = None

        return StatusConsultaSchema(
            numero_guia=guia.numero_guia,
            status_consulta=guia.status_consulta,
            data_ultima_consulta=guia.data_ultima_consulta,
            dados_retornados=dados_retornados,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status de consulta da guia {numero_guia}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/guias/consulta-externa/status", response_model=dict)
async def obter_estatisticas_consulta_externa(db: Session = Depends(get_db)):
    """
    Obtém estatísticas das consultas externas realizadas.

    Retorna contadores de guias por status de consulta e outras
    informações úteis para monitoramento.
    """
    try:
        # Contar guias por status de consulta
        total_guias = db.query(Guia).count()
        pendentes = db.query(Guia).filter(Guia.status_consulta == "P").count()
        consultadas = db.query(Guia).filter(Guia.status_consulta == "C").count()
        retornadas = db.query(Guia).filter(Guia.status_consulta == "R").count()

        # Guias com consulta recente (últimas 24h)
        from datetime import datetime, timedelta

        ontem = datetime.utcnow() - timedelta(days=1)
        consultas_recentes = (
            db.query(Guia).filter(Guia.data_ultima_consulta >= ontem).count()
        )

        # URLs mais utilizadas (removido - agora é configuração global)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "estatisticas": {
                "total_guias": total_guias,
                "pendentes": pendentes,
                "consultadas": consultadas,
                "retornadas": retornadas,
                "consultas_recentes_24h": consultas_recentes,
            },
            "configuracoes": {
                "timeout_ms": get_settings().CONSULTA_EXTERNA_TIMEOUT_MS,
                "intervalo_ms": get_settings().CONSULTA_EXTERNA_INTERVALO_MS,
                "max_tentativas": get_settings().CONSULTA_EXTERNA_MAX_TENTATIVAS,
                "url_consulta_externa": get_settings().CONSULTA_EXTERNA_URL,
            },
        }

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de consulta externa: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ROTAS DE MONITORAMENTO DE CAMPOS
# =============================================================================


@router.post("/monitor-campos/executar", response_model=dict)
@limiter.limit(f"{get_settings().RATE_LIMIT_MONITOR_MINUTES}/minute")
async def executar_monitoramento_campos(
    request: Request, db: Session = Depends(get_db)
):
    """
    Executa monitoramento de campos de guias manualmente.

    Esta rota permite executar o monitoramento de campos de forma manual,
    verificando mudanças nas guias que estão sendo monitoradas.
    """
    try:
        monitor_service = MonitorCamposService()
        resultado = await monitor_service.monitorar_guias()

        return {
            "sucesso": resultado["sucesso"],
            "mensagem": "Monitoramento executado com sucesso",
            "dados": resultado,
        }

    except Exception as e:
        logger.error(f"Erro ao executar monitoramento de campos: {e}")
        raise HTTPException(
            status_code=500,
            detail={"sucesso": False, "erro": f"Erro interno: {str(e)}"},
        )


@router.get("/monitor-campos/estatisticas", response_model=dict)
async def obter_estatisticas_monitoramento_campos(db: Session = Depends(get_db)):
    """
    Obtém estatísticas do monitoramento de campos.

    Retorna informações sobre guias em monitoramento, finalizadas
    e outras métricas úteis para acompanhamento.
    """
    try:
        monitor_service = MonitorCamposService()
        estatisticas = monitor_service.obter_estatisticas_monitoramento()

        return estatisticas

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas de monitoramento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitor-campos/guias/{status}", response_model=dict)
async def obter_guias_por_status_monitoramento(
    status: str = Path(..., description="Status de monitoramento (N/M/F)"),
    db: Session = Depends(get_db),
):
    """
    Obtém guias por status de monitoramento.

    Retorna lista de guias filtradas por status de monitoramento:
    - N: Não monitorando
    - M: Monitorando
    - F: Finalizado
    """
    try:
        if status not in ["N", "M", "F"]:
            raise HTTPException(
                status_code=400,
                detail="Status deve ser N (Não monitorando), M (Monitorando) ou F (Finalizado)",
            )

        guias = db.query(Guia).filter(Guia.status_monitoramento == status).all()

        return {
            "status_monitoramento": status,
            "total_guias": len(guias),
            "guias": [
                {
                    "numero_guia": guia.numero_guia,
                    "situacao_guia": guia.situacao_guia,
                    "tp_status": guia.tp_status,
                    "data_atualizacao": (
                        guia.data_atualizacao.isoformat()
                        if guia.data_atualizacao
                        else None
                    ),
                    "data_ultima_consulta": (
                        guia.data_ultima_consulta.isoformat()
                        if guia.data_ultima_consulta
                        else None
                    ),
                    "tentativas": guia.tentativas,
                }
                for guia in guias
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter guias por status de monitoramento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitor-campos/start", response_model=dict)
async def iniciar_monitoramento_campos():
    """
    Inicia o monitoramento automático de campos de guias.
    """
    try:
        from app.services.monitor_campos_service import monitor_campos_service

        # Verificar se já está rodando
        if (
            hasattr(monitor_campos_service, "_running")
            and monitor_campos_service._running
        ):
            return {
                "sucesso": False,
                "mensagem": "Monitoramento de campos já está em execução",
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Iniciar monitoramento contínuo em background
        import asyncio

        monitor_campos_service._running = True
        monitor_campos_service._task = asyncio.create_task(
            monitor_campos_service.iniciar_monitoramento_continuo()
        )

        return {
            "sucesso": True,
            "mensagem": "Monitoramento de campos iniciado com sucesso",
            "configuracoes": {
                "intervalo_minutos": monitor_campos_service.intervalo_monitoramento,
                "campos_criticos": monitor_campos_service.campos_criticos,
                "status_final": monitor_campos_service.status_final,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Erro ao iniciar monitoramento de campos: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "sucesso": False,
                "erro": f"Erro interno: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@router.post("/monitor-campos/stop", response_model=dict)
async def parar_monitoramento_campos():
    """
    Para o monitoramento automático de campos de guias.
    """
    try:
        from app.services.monitor_campos_service import monitor_campos_service

        # Verificar se está rodando
        if (
            not hasattr(monitor_campos_service, "_running")
            or not monitor_campos_service._running
        ):
            return {
                "sucesso": False,
                "mensagem": "Monitoramento de campos não está em execução",
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Parar monitoramento
        monitor_campos_service._running = False
        if hasattr(monitor_campos_service, "_task") and monitor_campos_service._task:
            monitor_campos_service._task.cancel()
            try:
                await monitor_campos_service._task
            except asyncio.CancelledError:
                pass

        return {
            "sucesso": True,
            "mensagem": "Monitoramento de campos parado com sucesso",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Erro ao parar monitoramento de campos: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "sucesso": False,
                "erro": f"Erro interno: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@router.get("/monitor-campos/status", response_model=dict)
async def obter_status_monitoramento_campos():
    """
    Obtém o status do monitoramento de campos de guias.
    """
    try:
        from app.services.monitor_campos_service import monitor_campos_service

        # Verificar se está rodando
        running = (
            hasattr(monitor_campos_service, "_running")
            and monitor_campos_service._running
        )

        return {
            "monitoramento_ativo": running,
            "configuracoes": {
                "intervalo_minutos": monitor_campos_service.intervalo_monitoramento,
                "campos_criticos": monitor_campos_service.campos_criticos,
                "status_final": monitor_campos_service.status_final,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Erro ao obter status do monitoramento de campos: {e}")
        raise HTTPException(status_code=500, detail=str(e))
