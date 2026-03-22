from sqlalchemy import Integer, String, Column, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from core.database import base
from datetime import datetime

class Notification(base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    company = relationship("Company", back_populates="company_messages")
    type = Column(String)
    data = Column(JSONB)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)