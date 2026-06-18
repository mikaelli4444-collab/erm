from sqlalchemy import Integer, Column, ForeignKey
from sqlalchemy.orm import relationship
from core.database import base


class Moduls_Companies(base):
    __tablename__ = 'moduls_companies'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    modul_id = Column(Integer, ForeignKey('moduls.id'), nullable=False)
    modul = relationship("Moduls", back_populates="company_moduls")
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship("Company", back_populates="moduls_company")