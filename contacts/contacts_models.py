from sqlalchemy import Integer, String, Column, ForeignKey
from sqlalchemy.orm import relationship
from core.database import base
class Contacts(base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)  # personal, architect, client, employed...
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="contacts")
    payments = relationship("Receivable", back_populates="payer")