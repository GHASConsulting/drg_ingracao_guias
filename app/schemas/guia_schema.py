from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import List, Optional, Union
from decimal import Decimal


class AnexoSchema(BaseModel):
    """Schema para validação de anexos."""

    numero_lote_documento: str = Field(..., min_length=1, max_length=20)
    numero_protocolo_documento: str = Field(..., min_length=1, max_length=20)
    formato_documento: str = Field(..., pattern=r"^(PDF|JPG|PNG|DOC)$")
    sequencial_documento: str = Field(..., min_length=1, max_length=10)
    data_criacao: date
    nome: str = Field(..., min_length=1, max_length=255)
    url_documento: str = Field(..., pattern=r"^https?://")
    observacao_documento: Optional[str] = Field(None, max_length=500)
    tipo_documento: str = Field(..., min_length=1, max_length=2)

    class Config:
        from_attributes = True


class ProcedimentoSchema(BaseModel):
    """Schema para validação de procedimentos."""

    tabela: str = Field(..., pattern=r"^(TUSS|CBHPM|SIGTAP)$")
    codigo: str = Field(..., min_length=1, max_length=15)
    descricao: str = Field(..., min_length=1, max_length=255)
    qtde_solicitada: int = Field(..., ge=1)
    valor_unitario: Decimal = Field(..., ge=0, decimal_places=2)
    qtde_autorizada: int = Field(..., ge=1)

    class Config:
        from_attributes = True


class DiagnosticoSchema(BaseModel):
    """Schema para validação de diagnósticos."""

    codigo: str = Field(..., min_length=3, max_length=10)
    tipo: str = Field(..., pattern=r"^[1-3]$")

    class Config:
        from_attributes = True


class GuiaSchema(BaseModel):
    """Schema para validação de guias de internação."""

    # Campos principais
    codigo_operadora: str = Field(..., min_length=1, max_length=6)
    numero_guia: str = Field(..., min_length=1, max_length=20)
    numero_guia_operadora: Optional[str] = Field(None, max_length=20)
    numero_guia_internacao: Optional[str] = Field(None, max_length=20)
    data_autorizacao: date
    senha: Optional[str] = Field(None, max_length=20)
    data_validade: Optional[date] = None

    # Dados do beneficiário
    numero_carteira: str = Field(..., min_length=1, max_length=20)
    data_validade_carteira: Optional[date] = None
    rn: Optional[str] = Field(None, pattern=r"^[SN]$")
    data_nascimento: date
    sexo: str = Field(..., pattern=r"^[MFI]$")
    situacao_beneficiario: str = Field(..., pattern=r"^[AI]$")
    nome_beneficiario: str = Field(..., min_length=1, max_length=100)

    # Dados do prestador
    codigo_prestador: str = Field(..., min_length=1, max_length=14)
    nome_prestador: str = Field(..., min_length=1, max_length=70)
    nome_profissional: Optional[str] = Field(None, max_length=70)
    codigo_profissional: str = Field(..., min_length=1, max_length=2)
    numero_registro_profissional: str = Field(..., min_length=1, max_length=15)
    uf_profissional: str = Field(..., min_length=2, max_length=2)
    codigo_cbo: str = Field(..., min_length=4, max_length=6)

    # Dados do hospital
    codigo_contratado: str = Field(..., min_length=1, max_length=14)
    nome_hospital: str = Field(..., min_length=1, max_length=70)
    data_sugerida_internacao: date
    carater_atendimento: str = Field(..., pattern=r"^[1-5]$")
    tipo_internacao: str = Field(..., pattern=r"^[1-5]$")
    regime_internacao: str = Field(..., pattern=r"^[1-5]$")
    diarias_solicitadas: int = Field(..., ge=1, le=365)
    previsao_uso_opme: Optional[str] = Field(None, pattern=r"^[SN]$")
    previsao_uso_quimioterapico: Optional[str] = Field(None, pattern=r"^[SN]$")
    indicacao_clinica: str = Field(..., min_length=1, max_length=1000)
    indicacao_acidente: str = Field(..., pattern=r"^[0-2]$")
    tipo_acomodacao_solicitada: Optional[str] = Field(None, pattern=r"^[1-2]$")

    # Dados da autorização
    data_admissao_estimada: Optional[date] = None
    qtde_diarias_autorizadas: Optional[int] = Field(None, ge=1, le=365)
    tipo_acomodacao_autorizada: Optional[str] = Field(None, pattern=r"^[1-2]$")
    cnes_autorizado: Optional[str] = Field(None, max_length=7)
    observacao_guia: Optional[str] = Field(None, max_length=1000)
    data_solicitacao: date
    justificativa_operadora: Optional[str] = Field(None, max_length=1000)

    # Dados complementares
    natureza_guia: str = Field(..., pattern=r"^[1-6]$")
    guia_complementar: str = Field(..., pattern=r"^[SN]$")
    situacao_guia: str = Field(..., pattern=r"^[APNCS]$")
    tipo_doenca: Optional[str] = Field(None, pattern=r"^[1-2]$")
    tempo_doenca: Optional[int] = Field(None, ge=1, le=999)
    longa_permanencia: Optional[str] = Field(None, pattern=r"^[1-2]$")
    motivo_encerramento: Optional[str] = Field(None, pattern=r"^[1-5]$|^9$")
    tipo_alta: Optional[str] = Field(None, pattern=r"^[1-8]$")
    data_alta: Optional[date] = None

    # Relacionamentos
    anexo: Optional[List[AnexoSchema]] = None
    procedimento: Optional[List[ProcedimentoSchema]] = None
    diagnostico: Optional[List[DiagnosticoSchema]] = None

    class Config:
        from_attributes = True


class LoteGuiasSchema(BaseModel):
    """Schema para validação do lote de guias."""

    guia: List[GuiaSchema] = Field(..., min_items=1)

    class Config:
        from_attributes = True


class EntradaSchema(BaseModel):
    """Schema para validação da estrutura completa de entrada."""

    loteGuias: LoteGuiasSchema

    @field_validator("loteGuias", mode="after")
    @classmethod
    def validate_lote_size(cls, v):
        """Valida se o lote não excede o limite de tamanho."""
        import json

        # Converter para JSON para calcular tamanho
        json_str = json.dumps(v.model_dump(), default=str)
        size_kb = len(json_str.encode("utf-8")) / 1024

        if size_kb > 500:  # Limite de 500KB
            raise ValueError(
                f"Lote excede o limite de 500KB. Tamanho atual: {size_kb:.2f}KB"
            )

        return v

    class Config:
        from_attributes = True


# Schemas de resposta
class GuiaResponseSchema(BaseModel):
    """Schema para resposta de guias."""

    id: int
    numero_guia: str
    codigo_operadora: str
    data_autorizacao: Optional[Union[date, str]] = None
    situacao_guia: str
    tp_status: str
    data_processamento: Optional[Union[datetime, str]] = None
    mensagem_erro: Optional[str] = None
    tentativas: int
    data_criacao: Optional[Union[datetime, str]] = None

    class Config:
        from_attributes = True

    @field_validator("data_autorizacao", mode="before")
    @classmethod
    def format_data_autorizacao(cls, v):
        if v is None:
            return None
        if isinstance(v, date):
            return v.isoformat()
        return v

    @field_validator("data_processamento", mode="before")
    @classmethod
    def format_data_processamento(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    @field_validator("data_criacao", mode="before")
    @classmethod
    def format_data_criacao(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class StatusResponseSchema(BaseModel):
    """Schema para resposta de status."""

    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True
