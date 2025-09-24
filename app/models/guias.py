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
    numero_guia = Column(String(20), unique=True, nullable=False, index=True)
    codigo_operadora = Column(String(6), nullable=False)
    numero_guia_operadora = Column(String(20))
    numero_guia_internacao = Column(String(20))
    data_autorizacao = Column(Date, nullable=False)
    senha = Column(String(20))
    data_validade = Column(Date)

    # Dados do beneficiário
    numero_carteira = Column(String(20), nullable=False)
    data_validade_carteira = Column(Date)
    rn = Column(String(1))  # S/N
    data_nascimento = Column(DateTime, nullable=False)
    sexo = Column(String(1), nullable=False)  # M/F/I
    situacao_beneficiario = Column(String(1), nullable=False)  # A/I

    # Dados do prestador
    codigo_prestador = Column(String(14), nullable=False)
    nome_prestador = Column(String(70), nullable=False)
    nome_profissional = Column(String(70))
    codigo_profissional = Column(String(2), nullable=False)
    numero_registro_profissional = Column(String(15), nullable=False)
    uf_profissional = Column(String(2), nullable=False)
    codigo_cbo = Column(String(6), nullable=False)

    # Dados do hospital
    codigo_contratado = Column(String(14), nullable=False)
    nome_hospital = Column(String(70), nullable=False)
    data_sugerida_internacao = Column(Date, nullable=False)
    carater_atendimento = Column(String(1), nullable=False)  # 1-5
    tipo_internacao = Column(String(1), nullable=False)  # 1-5
    regime_internacao = Column(String(1), nullable=False)  # 1-5
    diarias_solicitadas = Column(Integer, nullable=False)
    previsao_uso_opme = Column(String(1))  # S/N
    previsao_uso_quimioterapico = Column(String(1))  # S/N
    indicacao_clinica = Column(Text, nullable=False)
    indicacao_acidente = Column(String(1), nullable=False)  # 0-2
    tipo_acomodacao_solicitada = Column(String(2))  # 1-2

    # Dados da autorização
    data_admissao_estimada = Column(Date)
    qtde_diarias_autorizadas = Column(Integer)
    tipo_acomodacao_autorizada = Column(String(2))
    cnes_autorizado = Column(String(7))
    observacao_guia = Column(Text)
    data_solicitacao = Column(Date, nullable=False)
    justificativa_operadora = Column(Text)

    # Dados complementares
    natureza_guia = Column(String(1), nullable=False)  # 1-6
    guia_complementar = Column(String(1), nullable=False)  # S/N
    situacao_guia = Column(String(2), nullable=False)  # A/P/N/C/S
    tipo_doenca = Column(String(1))  # 1-2
    tempo_doenca = Column(Integer)
    longa_permanencia = Column(String(1))  # 1-2
    motivo_encerramento = Column(String(2))  # 1-5,9
    tipo_alta = Column(String(2))  # 1-8
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
