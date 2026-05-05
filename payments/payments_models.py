from sqlalchemy import Integer, String, Column, ForeignKey, Boolean, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from core.database import base
from datetime import date
from core.enum.enum import plansEnum, subscriptionStatusEnum

class Subscription(base):
    __tablename__ = 'subscription'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship("User", back_populates="subscription")
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True, index=True)
    plan = relationship("Plans", back_populates="plan_subscription")
    start_date = Column(Date, default=date.today, nullable=False)
    end_date = Column(Date, nullable=True)
    active = Column(Boolean, default=False, nullable=False)
    amount = Column(Integer, nullable=False)
    mp_payment_id = Column(String, nullable=True)
    status = Column(SQLEnum(subscriptionStatusEnum), default=subscriptionStatusEnum.pending.value, nullable=False) #pending, active, cancelled, expired
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    company = relationship("Company", back_populates="company_subscription")
    
class Plans(base):
    __tablename__ = 'plans'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mp_plan_id = Column(String, nullable=False, index=True)
    name = Column(SQLEnum(plansEnum), nullable=False, index=True)
    amount = Column(Integer, nullable=False, index=True)
    frequency = Column(Integer, nullable=False, index=True)
    currency = Column(String, nullable=False, default="BRL", index=True) #siempre va a ser BRL no jodas
    plan_subscription = relationship("Subscription", back_populates="plan") 