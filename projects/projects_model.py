from sqlalchemy import Integer, String, Column, ForeignKey, Boolean, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from core.database import base
from datetime import date
from core.enum.enum import StatusEnum

class Projects(base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    carpenter_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    carpenter = relationship("User", back_populates="carpenter_projects")
    client_name =  Column(String, nullable=True, index=True)
    delivery = Column(Date, default=date.today, nullable=False, index=True)
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.planning, nullable=False, index=True)
    photo_path = Column(String, index=True, nullable=True)
    pdf_path = Column(String, index=True, nullable=True)
    created_at = Column(Date, default=date.today, nullable=False)
    pdf_url = Column(String, index=True, nullable=True)
    description = Column(String, nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="company_projects")
    active = Column(Boolean, default=False, nullable=False, index=True) #esto es para decir si el proyecto ya se esta ejecutando en la fabrica o no
    address = Column(String, nullable=True, index=True) #direccion del cliente
    
    #guardar fotos y pdfs en un bucket de s3 y guardar las urls en la base de datos, para no sobrecargar la base de datos con archivos grandes
    #usar cloudflare r2 para guardar los archivos, es mas barato que s3