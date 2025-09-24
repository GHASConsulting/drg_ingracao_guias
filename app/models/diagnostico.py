from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base


class Diagnostico(Base):
    """Modelo para diagnósticos das guias."""

    __tablename__ = "inovemed_tbl_diagnosticos"

    # Campos principais
    id = Column(Integer, primary_key=True)
    codigo = Column(String(4), nullable=False)  # CID-10
    tipo = Column(String(1), nullable=False)  # P/S

    # Chave estrangeira
    guia_id = Column(Integer, ForeignKey("inovemed_tbl_guias.id"), nullable=False)

    # Relacionamento
    guia = relationship("Guia", back_populates="diagnosticos")

    def __repr__(self):
        return f"<Diagnostico {self.codigo}>"

    def to_dict(self):
        """Converte o modelo para dicionário."""
        return {
            "id": self.id,
            "codigo": self.codigo,
            "tipo": self.tipo,
            "guia_id": self.guia_id,
        }
