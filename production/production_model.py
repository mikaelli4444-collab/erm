from sqlalchemy import Integer, String, Date, Column, ForeignKey
from sqlalchemy.orm import relationship
from core.database import base


class Production(base):
    __tablename__ = 'production'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_name = Column(String, index=True, nullable=False)
    project_name = Column(String, nullable=False)
    delivery_date = Column(Date, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="productions")

# 3. Dica de Ouro: Interface HTML
# Se sua interface for um formulário HTML, use <input type="date">.
# O navegador mostrará o formato local para o usuário (ex: DD/MM/YYYY no Brasil/LatAm).
# Mas o navegador sempre enviará para o seu Python no formato YYYY-MM-DD por padrão. MDN Web Docs - Input Date.
# Qual dessas opções se encaixa melhor no seu projeto? Se estiver usando um formulário HTML, a opção 3 é a mais fácil de todas.
