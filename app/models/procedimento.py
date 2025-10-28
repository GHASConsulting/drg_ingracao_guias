from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Procedimento(Base):
    """Modelo para procedimentos das guias."""

    __tablename__ = "inovemed_tbl_procedimentos"

    # Campos principais
    id = Column(Integer, primary_key=True)
    tabela = Column(String(2), nullable=False)  # 00, 20, 22, 98
    codigo = Column(
        String(10), nullable=False
    )  # Código identificador do procedimento ou item assistencial solicitado, conforme a tabela de referência (ex: TUSS)
    descricao = Column(String(150), nullable=False)
    qtde_solicitada = Column(Integer, nullable=False)
    valor_unitario = Column(
        Numeric(8, 2), nullable=False
    )  # Valor unitário do procedimento ou item solicitado (formato 8,2 - "." para casas decimais)
    qtde_autorizada = Column(
        Integer, nullable=False
    )  # Quantidade do procedimento ou item autorizada pela operadora (caso não autorize deve ser informado zero)

    # Chave estrangeira
    guia_id = Column(Integer, ForeignKey("inovemed_tbl_guias.id"), nullable=False)

    # Relacionamento
    guia = relationship("Guia", back_populates="procedimentos")

    def __repr__(self):
        return f"<Procedimento {self.codigo}>"

    def to_dict(self):
        """Converte o modelo para dicionário."""
        return {
            "id": self.id,
            "tabela": self.tabela,
            "codigo": self.codigo,
            "descricao": self.descricao,
            "qtde_solicitada": self.qtde_solicitada,
            "valor_unitario": (
                float(self.valor_unitario) if self.valor_unitario else None
            ),
            "qtde_autorizada": self.qtde_autorizada,
            "guia_id": self.guia_id,
        }
