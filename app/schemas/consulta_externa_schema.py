#!/usr/bin/env python3
"""
Schemas para consulta externa de guias
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class ConsultaExternaRequestSchema(BaseModel):
    """Schema para requisição de consulta externa"""

    numero_guia: str = Field(
        ..., min_length=1, max_length=20, description="Número da guia"
    )
    data_ultima_atualizacao: Optional[datetime] = Field(
        None, description="Data da última atualização da guia (opcional)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "numero_guia": "R679542",
                "data_ultima_atualizacao": "2024-01-15T10:30:00Z",
            }
        }


class ConsultaExternaResponseSchema(BaseModel):
    """Schema para resposta de consulta externa"""

    sucesso: bool = Field(..., description="Indica se a consulta foi bem-sucedida")
    mensagem: Optional[str] = Field(None, description="Mensagem de retorno")
    dados: Optional[dict] = Field(
        None, description="Dados retornados da consulta externa"
    )
    status_consulta: str = Field(..., description="Status da consulta (P/C/R)")
    numero_guia: str = Field(..., description="Número da guia consultada")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp da consulta"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "mensagem": "Consulta realizada com sucesso",
                "dados": {
                    "aprovada": True,
                    "numero_autorizacao": "AUT123456",
                    "data_aprovacao": "2024-01-15T14:30:00Z",
                },
                "status_consulta": "R",
                "numero_guia": "R679542",
                "timestamp": "2024-01-15T14:30:00Z",
            }
        }


class ConsultaMultiplaRequestSchema(BaseModel):
    """Schema para consulta múltipla de guias"""

    guias: List[dict] = Field(
        ..., min_items=1, description="Lista de guias para consultar"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "guias": [
                    {
                        "numero_guia": "R679542",
                        "data_ultima_atualizacao": "2024-01-15T10:30:00Z",
                    },
                    {
                        "numero_guia": "R679543",
                        "data_ultima_atualizacao": "2024-01-15T11:00:00Z",
                    },
                ],
            }
        }


class ConsultaMultiplaResponseSchema(BaseModel):
    """Schema para resposta de consulta múltipla"""

    sucesso: bool = Field(
        ..., description="Indica se todas as consultas foram bem-sucedidas"
    )
    total_processadas: int = Field(..., description="Total de guias processadas")
    sucessos: int = Field(..., description="Número de consultas bem-sucedidas")
    erros: int = Field(..., description="Número de consultas com erro")
    resultados: List[dict] = Field(
        ..., description="Resultados individuais de cada consulta"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp da consulta"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "sucesso": True,
                "total_processadas": 2,
                "sucessos": 2,
                "erros": 0,
                "resultados": [
                    {
                        "numero_guia": "R679542",
                        "sucesso": True,
                        "mensagem": "Consulta realizada com sucesso",
                        "status_consulta": "R",
                    },
                    {
                        "numero_guia": "R679543",
                        "sucesso": True,
                        "mensagem": "Consulta realizada com sucesso",
                        "status_consulta": "R",
                    },
                ],
                "timestamp": "2024-01-15T14:30:00Z",
            }
        }


class StatusConsultaSchema(BaseModel):
    """Schema para status de consulta de guia"""

    numero_guia: str = Field(..., description="Número da guia")
    status_consulta: str = Field(..., description="Status da consulta (P/C/R)")
    data_ultima_consulta: Optional[datetime] = Field(
        None, description="Data da última consulta"
    )
    dados_retornados: Optional[dict] = Field(
        None, description="Dados retornados da última consulta"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "numero_guia": "R679542",
                "status_consulta": "R",
                "data_ultima_consulta": "2024-01-15T14:30:00Z",
                "dados_retornados": {
                    "aprovada": True,
                    "numero_autorizacao": "AUT123456",
                },
            }
        }
