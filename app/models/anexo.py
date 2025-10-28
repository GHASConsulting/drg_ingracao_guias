from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Anexo(Base):
    """Modelo para anexos das guias."""

    __tablename__ = "inovemed_tbl_anexos"

    # Campos principais
    id = Column(Integer, primary_key=True)
    numero_lote_documento = Column(
        String(12)
    )  # Número do lote ao qual o documento se refere (preenchido quando envio se refere ao Lote Guias e/ou Recurso de glosa)
    numero_protocolo_documento = Column(
        String(12)
    )  # Número atribuído pela operadora ao lote de guias (preenchido quando envio se refere ao Lote Guias e/ou Recurso de glosa)
    formato_documento = Column(
        String(2), nullable=False
    )  # 1=PDF, 2=DOC, 3=XLS, 4=JPG, 5=PNG, 99=Outros
    sequencial_documento = Column(
        Integer
    )  # Número sequencial de referência do procedimento ou item assistencial (preenchido em caso de envio de documento referente a um item específico)
    data_criacao = Column(Date, nullable=False)
    nome = Column(String(500), nullable=False)  # Nome do arquivo (obrigatório)
    url_documento = Column(
        String(500), nullable=False
    )  # URL para download do documento (obrigatório)
    observacao_documento = Column(
        String(500)
    )  # Observação/Justificativa sobre o documento (campo opcional)
    tipo_documento = Column(
        String(2), nullable=False
    )  # 01=Laudo de exame, 02=Relatório médico, 03=Solicitação escrita, 04=Justificativa clínica, 99=Outros

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
