from sqlalchemy import Integer, String, Column, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from core.database import base
from datetime import datetime
from zoneinfo import ZoneInfo


class Inventory(base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    item_name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="inventory_items")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="company_items")
