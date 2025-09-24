from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Anexo(Base):
    """Modelo para anexos das guias."""

    __tablename__ = "inovemed_tbl_anexos"

    # Campos principais
    id = Column(Integer, primary_key=True)
    numero_lote_documento = Column(String(12))
    numero_protocolo_documento = Column(String(12))
    formato_documento = Column(String(2), nullable=False)  # 1-5, 99
    sequencial_documento = Column(Integer)
    data_criacao = Column(Date, nullable=False)
    nome = Column(String(500), nullable=False)
    url_documento = Column(String(500), nullable=False)
    observacao_documento = Column(String(500))
    tipo_documento = Column(String(2), nullable=False)  # 01-04, 99

    # Chave estrangeira
    guia_id = Column(Integer, ForeignKey("inovemed_tbl_guias.id"), nullable=False)

    # Relacionamento
    guia = relationship("Guia", back_populates="anexos")

    def __repr__(self):
        return f"<Anexo {self.nome}>"

    def to_dict(self):
        """Converte o modelo para dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "formato_documento": self.formato_documento,
            "tipo_documento": self.tipo_documento,
            "data_criacao": (
                self.data_criacao.isoformat() if self.data_criacao else None
            ),
            "guia_id": self.guia_id,
        }
