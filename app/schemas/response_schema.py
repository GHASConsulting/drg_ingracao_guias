from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class LogGuiaSchema(BaseModel):
    """Schema para validação do log individual de uma guia."""

    numero_guia: str = Field(..., min_length=1, max_length=20)
    situacao: str = Field(..., pattern=r"^[SP]$")
    erro: Optional[str] = Field(None, max_length=500)

    class Config:
        from_attributes = True


class LogGuiasSchema(BaseModel):
    """Schema para validação da lista de logs de guias."""

    guia: List[LogGuiaSchema]

    class Config:
        from_attributes = True


class LogInternacaoSchema(BaseModel):
    """Schema para validação do log de internação."""

    log_guias: LogGuiasSchema

    class Config:
        from_attributes = True


class ResponseSchema(BaseModel):
    """Schema para validação da resposta completa."""

    log_internacao: LogInternacaoSchema

    class Config:
        from_attributes = True


class ErrorResponseSchema(BaseModel):
    """Schema para validação de respostas de erro."""

    status: str = Field(..., pattern=r"^error$")
    message: str = Field(..., min_length=1, max_length=500)
    details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class SuccessResponseSchema(BaseModel):
    """Schema para validação de respostas de sucesso."""

    status: str = Field(..., pattern=r"^success$")
    message: str = Field(..., min_length=1, max_length=500)
    data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class SystemStatusResponseSchema(BaseModel):
    """Schema para validação de status do sistema."""

    status: str = Field(..., pattern=r"^(success|error)$")
    message: str = Field(..., min_length=1, max_length=500)
    version: str = Field(..., min_length=1, max_length=20)
    timestamp: datetime
    database_status: str = Field(..., pattern=r"^(connected|disconnected)$")
    celery_status: str = Field(..., pattern=r"^(running|stopped)$")
    queue_status: Dict[str, Any]

    class Config:
        from_attributes = True


class GuiaStatusSchema(BaseModel):
    """Schema para validação do status de uma guia específica."""

    id: int
    numero_guia: str
    codigo_operadora: str
    tp_status: str = Field(..., pattern=r"^[ATE]$")
    data_criacao: datetime
    data_processamento: Optional[datetime] = None
    mensagem_erro: Optional[str] = None
    tentativas: int = Field(..., ge=0, le=2)

    class Config:
        from_attributes = True


class ListaGuiasResponseSchema(BaseModel):
    """Schema para validação da resposta de lista de guias."""

    status: str = Field(..., pattern=r"^success$")
    data: List[GuiaStatusSchema]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1, le=100)

    class Config:
        from_attributes = True


class ProcessingStatsSchema(BaseModel):
    """Schema para validação das estatísticas de processamento."""

    total_guias: int = Field(..., ge=0)
    aguardando: int = Field(..., ge=0)
    processadas: int = Field(..., ge=0)
    com_erro: int = Field(..., ge=0)
    taxa_sucesso: float = Field(..., ge=0, le=100)
    ultima_atualizacao: datetime

    class Config:
        from_attributes = True


class StatsResponseSchema(BaseModel):
    """Schema para validação da resposta de estatísticas."""

    status: str = Field(..., pattern=r"^success$")
    message: str
    data: ProcessingStatsSchema

    class Config:
        from_attributes = True
