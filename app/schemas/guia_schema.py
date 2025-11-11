from pydantic import BaseModel, Field, field_validator, model_validator
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
    caminho_documento: str = Field(..., min_length=1, max_length=500)
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
    codigo_operadora: str = Field(
        ..., min_length=1, max_length=6, alias="codigoOperadora"
    )
    numero_guia: str = Field(..., min_length=1, max_length=20, alias="numeroGuia")
    numero_guia_operadora: Optional[str] = Field(
        None, max_length=20, alias="numeroGuiaOperadora"
    )
    numero_guia_internacao: Optional[str] = Field(
        None, max_length=20, alias="numeroGuiaInternacao"
    )
    data_autorizacao: date = Field(alias="dataAutorizacao")
    senha: Optional[str] = Field(None, max_length=20)
    data_validade: Optional[date] = Field(None, alias="dataValidade")

    # Dados do beneficiário
    numero_carteira: str = Field(
        ..., min_length=1, max_length=20, alias="numeroCarteira"
    )
    data_validade_carteira: Optional[date] = Field(None, alias="dataValidadeCarteira")
    rn: Optional[str] = Field(None, pattern=r"^[SN]$")
    data_nascimento: date = Field(alias="dataNascimento")
    sexo: str = Field(..., pattern=r"^[MFI]$")
    situacao_beneficiario: str = Field(
        ..., pattern=r"^[AI]$", alias="situacaoBeneficiario"
    )
    nome_beneficiario: str = Field(
        ..., min_length=1, max_length=100, alias="nomeBeneficiario"
    )

    # Dados do prestador
    codigo_prestador: str = Field(
        ..., min_length=1, max_length=14, alias="codigoPrestador"
    )
    nome_prestador: str = Field(..., min_length=1, max_length=70, alias="nomePrestador")
    nome_profissional: Optional[str] = Field(
        None, max_length=70, alias="nomeProfissional"
    )
    codigo_profissional: str = Field(
        ..., min_length=1, max_length=2, alias="codigoProfissional"
    )
    numero_registro_profissional: str = Field(
        ..., min_length=1, max_length=15, alias="numeroRegistroProfissional"
    )
    uf_profissional: str = Field(
        ..., min_length=2, max_length=2, alias="ufProfissional"
    )
    codigo_cbo: str = Field(..., min_length=4, max_length=6, alias="codigoCbo")

    # Dados do hospital
    codigo_contratado: str = Field(
        ..., min_length=1, max_length=14, alias="codigoContratado"
    )
    nome_hospital: str = Field(..., min_length=1, max_length=70, alias="nomeHospital")
    data_sugerida_internacao: date = Field(alias="dataSugeridaInternacao")
    carater_atendimento: str = Field(
        ..., pattern=r"^[1-5]$", alias="caraterAtendimento"
    )
    tipo_internacao: str = Field(..., pattern=r"^[1-5]$", alias="tipoInternacao")
    regime_internacao: str = Field(..., pattern=r"^[1-5]$", alias="regimeInternacao")
    diarias_solicitadas: int = Field(..., ge=1, le=365, alias="diariasSolicitadas")
    previsao_uso_opme: Optional[str] = Field(
        None, pattern=r"^[SN]$", alias="previsaoUsoOpme"
    )
    previsao_uso_quimioterapico: Optional[str] = Field(
        None, pattern=r"^[SN]$", alias="previsaoUsoQuimioterapico"
    )
    indicacao_clinica: str = Field(
        ..., min_length=1, max_length=1000, alias="indicacaoClinica"
    )
    indicacao_acidente: str = Field(..., pattern=r"^[0-2]$", alias="indicacaoAcidente")
    tipo_acomodacao_solicitada: Optional[str] = Field(
        None, pattern=r"^[1-2]$", alias="tipoAcomodacaoSolicitada"
    )

    # Dados da autorização
    data_admissao_estimada: Optional[date] = Field(None, alias="dataAdmissaoEstimada")
    qtde_diarias_autorizadas: Optional[int] = Field(
        None, ge=1, le=365, alias="qtdeDiariasAutorizadas"
    )
    tipo_acomodacao_autorizada: Optional[str] = Field(
        None, pattern=r"^[1-2]$", alias="tipoAcomodacaoAutorizada"
    )
    cnes_autorizado: Optional[str] = Field(None, max_length=7, alias="cnesAutorizado")
    observacao_guia: Optional[str] = Field(
        None, max_length=1000, alias="observacaoGuia"
    )
    data_solicitacao: date = Field(alias="dataSolicitacao")
    justificativa_operadora: Optional[str] = Field(
        None, max_length=1000, alias="justificativaOperadora"
    )

    # Dados complementares
    natureza_guia: str = Field(..., pattern=r"^[1-6]$", alias="naturezaGuia")
    guia_complementar: str = Field(..., pattern=r"^[SN]$", alias="guiaComplementar")
    situacao_guia: str = Field(..., pattern=r"^[APNCS]$", alias="situacaoGuia")
    tipo_doenca: Optional[str] = Field(None, pattern=r"^[1-2]$", alias="tipoDoenca")
    tempo_doenca: Optional[int] = Field(None, ge=1, le=999, alias="tempoDoenca")
    longa_permanencia: Optional[str] = Field(
        None, pattern=r"^[1-2]$", alias="longaPermanencia"
    )
    motivo_encerramento: Optional[str] = Field(
        None, pattern=r"^[1-5]$|^9$", alias="motivoEncerramento"
    )
    tipo_alta: Optional[str] = Field(None, pattern=r"^[1-8]$", alias="tipoAlta")
    data_alta: Optional[date] = Field(None, alias="dataAlta")

    # Relacionamentos
    anexo: Optional[List[AnexoSchema]] = None
    procedimento: Optional[List[ProcedimentoSchema]] = None
    diagnostico: Optional[List[DiagnosticoSchema]] = None

    # Campos extras do JSON
    porte_hospital: Optional[str] = Field(None, alias="porteHospital")
    complexidade_hospital: Optional[str] = Field(None, alias="complexidadeHospital")
    esfera_administrativa: Optional[str] = Field(None, alias="esferaAdministrativa")
    endereco_hospital: Optional[str] = Field(None, alias="enderecoHospital")

    @model_validator(mode="after")
    def validate_numero_guia_internacao_obrigatorio(self):
        """Valida se numero_guia_internacao é obrigatório quando guia_complementar = 'S'."""
        # Se guia_complementar = 'S', numero_guia_internacao deve ser preenchido
        if self.guia_complementar == "S":
            if (
                not self.numero_guia_internacao
                or self.numero_guia_internacao.strip() == ""
            ):
                raise ValueError(
                    "O campo 'numero_guia_internacao' é obrigatório quando 'guia_complementar' = 'S'"
                )

        return self

    class Config:
        from_attributes = True
        populate_by_name = True


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
