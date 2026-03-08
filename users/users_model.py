from sqlalchemy import Integer, String, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.database import base
from datetime import datetime

class User(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    fullname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)
    is_verified = Column(Integer, default=0, nullable=False)
    verification_code = Column(String, nullable=True)
    verification_code_expires_at = Column(DateTime, nullable=True)
    inventory_items = relationship("Inventory", back_populates="owner")
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="owner", foreign_keys=[company_id])

class Company(base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    legal_name = Column(String, index=True, nullable=False)
    tax_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    plan = Column(String, default='basic', nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", foreign_keys=[owner_id])
    company_items = relationship("Inventory", back_populates="company")