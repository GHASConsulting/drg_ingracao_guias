from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    Date,
)
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime


class Guia(Base):
    """Modelo para guias de internação"""

    __tablename__ = "inovemed_tbl_guias"

    # Campos principais
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_guia = Column(
        String(20), unique=True, nullable=False, index=True
    )  # Identificação da guia no prestador (Nº da guia no prestador)
    codigo_operadora = Column(
        String(6), nullable=False
    )  # Código da operadora na ANS (Registro ANS)
    numero_guia_operadora = Column(
        String(20)
    )  # Número atribuído pela operadora (deve ser preenchido caso a operadora atribua outro número à guia, independente do número que a identifica no prestador)
    numero_guia_internacao = Column(
        String(20)
    )  # Número da guia de solicitação de internação (deve ser preenchido em caso de guia complementar/prorrogação)
    data_autorizacao = Column(
        Date, nullable=False
    )  # Data em que a autorização foi concedida (formato AAAA-MM-DD)
    senha = Column(
        String(20)
    )  # Senha de autorização fornecida (deve ser preenchido em caso de autorização pela operadora com emissão de senha)
    data_validade = Column(
        Date
    )  # Validade da senha de autorização (formato AAAA-MM-DD - deve ser preenchido em caso de autorização pela operadora com emissão de senha com prazo de validade)

    # Dados do beneficiário
    numero_carteira = Column(
        String(20), nullable=False
    )  # Número da carteirinha do beneficiário
    data_validade_carteira = Column(
        Date
    )  # Validade da carteira do beneficiário (formato AAAA-MM-DD - deve ser informado somente quando for utilizada a contingência em papel e quando a operadora exigir autorização prévia para o procedimento e tal autorização não puder ser obtida)
    rn = Column(
        String(1)
    )  # Indicador de atendimento ao recém-nato (S=sim caso o atendimento seja do recém-nato e o beneficiário seja o responsável, N=não quando o atendimento for do próprio beneficiário)
    data_nascimento = Column(
        DateTime, nullable=False
    )  # Data completa de nascimento do beneficiário (formato AAAA-MM-DD HH:mm - yyyy=ano 4 dígitos, MM=mês 2 dígitos, dd=dia 2 dígitos, HH=hora 2 dígitos 00-23, mm=minuto 2 dígitos 00-59)
    sexo = Column(String(1), nullable=False)  # M/F/I
    situacao_beneficiario = Column(
        String(1), nullable=False
    )  # Situação atual no plano de saúde (A=Ativo, I=Inativo)
    nome_beneficiario = Column(String(100), nullable=False)

    # Dados do prestador
    codigo_prestador = Column(
        String(14), nullable=False
    )  # Código identificador do prestador solicitante junto à operadora (código do contratado na operadora)
    nome_prestador = Column(String(70), nullable=False)
    nome_profissional = Column(String(70))
    codigo_profissional = Column(
        String(2), nullable=False
    )  # Código do conselho profissional do solicitante do procedimento ou item assistencial
    numero_registro_profissional = Column(
        String(15), nullable=False
    )  # Número de registro do profissional solicitante no respectivo Conselho Profissional
    uf_profissional = Column(
        String(2), nullable=False
    )  # Sigla da Unidade Federativa do Conselho Profissional do solicitante do procedimento ou item assistencial
    codigo_cbo = Column(
        String(6), nullable=False
    )  # Código na Classificação Brasileira de Ocupações do profissional solicitante do procedimento ou item assistencial

    # Dados do hospital
    codigo_contratado = Column(String(14), nullable=False)
    nome_hospital = Column(String(70), nullable=False)
    porte_hospital = Column(String(1), default="2")  # 1-4
    complexidade_hospital = Column(String(1), default="1")  # 1-3
    esfera_administrativa = Column(String(1), default="2")  # 1-3
    endereco_hospital = Column(Text, default="Endereço não informado")
    data_sugerida_internacao = Column(Date, nullable=False)
    carater_atendimento = Column(
        String(1), nullable=False
    )  # 1=Eletivo, 2=Urgência, 3=Emergência, 4=Internação, 5=Ambulatorial
    tipo_internacao = Column(
        String(1), nullable=False
    )  # 1=Clínica, 2=Cirúrgica, 3=Obstétrica, 4=Psiquiátrica, 5=Outras
    regime_internacao = Column(
        String(1), nullable=False
    )  # 1=Hospitalar, 2=Hospital-dia, 3=Domiciliar, 4=Internação em clínica especializada, 5=Outras
    diarias_solicitadas = Column(Integer, nullable=False)
    previsao_uso_opme = Column(
        String(1)
    )  # S=Sim (órtese/prótese/material especial), N=Não
    previsao_uso_quimioterapico = Column(String(1))  # S=Sim (quimioterápico), N=Não
    indicacao_clinica = Column(Text, nullable=False)
    indicacao_acidente = Column(String(1), nullable=False)  # 0-2
    tipo_acomodacao_solicitada = Column(String(2))  # 1-2

    # Dados da autorização
    data_admissao_estimada = Column(Date)
    qtde_diarias_autorizadas = Column(Integer)
    tipo_acomodacao_autorizada = Column(
        String(2)
    )  # 1=Enfermaria, 2=Apartamento (preenchido em caso de autorização)
    cnes_autorizado = Column(String(7))
    senha_autorizacao = Column(
        String(20)
    )  # Senha de autorização retornada pela consulta externa
    observacao_guia = Column(Text)
    data_solicitacao = Column(Date, nullable=False)
    justificativa_operadora = Column(Text)

    # Dados complementares
    natureza_guia = Column(
        String(1), nullable=False
    )  # 1=Consulta, 2=SP/SADT, 3=Internação, 4=Solicitação de Autorização, 5=Prorrogação, 6=Odontologia
    guia_complementar = Column(
        String(1), nullable=False
    )  # S=Sim (associada à guia principal), N=Não
    situacao_guia = Column(String(2), nullable=False)  # A/P/N/C/S
    tipo_doenca = Column(String(1))  # 1=Aguda, 2=Crônica
    tempo_doenca = Column(Integer)
    longa_permanencia = Column(String(1))  # 1=Sim (internação longa permanência), 2=Não
    motivo_encerramento = Column(
        String(2)
    )  # 1=Alta médica, 2=Óbito, 3=Evasão, 4=Transferência, 5=Permanência, 9=Outros motivos
    tipo_alta = Column(
        String(2)
    )  # 1=Cura, 2=Alívio, 3=Sem melhora, 4=Óbito, 5=Alta a pedido, 6=Alta por evasão, 7=Transferência, 8=Outros
    data_alta = Column(Date)

    # Campos de controle
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    tp_status = Column(String(1), nullable=False, default="A")  # A/T/E
    data_processamento = Column(DateTime)
    mensagem_erro = Column(Text)
    tentativas = Column(Integer, default=0)

    # Novos campos para consulta externa
    status_consulta = Column(
        String(1), nullable=False, default="P"
    )  # P= Pendente, C= Consultado, R= Retornado
    data_ultima_consulta = Column(DateTime)
    dados_retornados = Column(Text)  # JSON com dados retornados da consulta externa
    status_monitoramento = Column(
        String(1), nullable=False, default="N"
    )  # N= Não monitorando, M= Monitorando, F= Finalizado

    # Relacionamentos
    anexos = relationship("Anexo", back_populates="guia", cascade="all, delete-orphan")
    procedimentos = relationship(
        "Procedimento", back_populates="guia", cascade="all, delete-orphan"
    )
    diagnosticos = relationship(
        "Diagnostico", back_populates="guia", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Guia {self.numero_guia}>"

    def to_dict(self):
        """Converte o modelo para dicionário."""
        return {
            "id": self.id,
            "numero_guia": self.numero_guia,
            "codigo_operadora": self.codigo_operadora,
            "data_autorizacao": (
                self.data_autorizacao.isoformat() if self.data_autorizacao else None
            ),
            "situacao_guia": self.situacao_guia,
            "tp_status": self.tp_status,
            "data_processamento": (
                self.data_processamento.isoformat() if self.data_processamento else None
            ),
            "mensagem_erro": self.mensagem_erro,
            "tentativas": self.tentativas,
            "data_criacao": (
                self.data_criacao.isoformat() if self.data_criacao else None
            ),
        }
