from sqlalchemy import Integer, String, Column, DateTime, ForeignKey, DECIMAL, Boolean, Date, Computed, Enum as SQLEnum
from sqlalchemy.orm import relationship
from core.database import base
from datetime import datetime
from zoneinfo import ZoneInfo
    
class WeeklySchedule(base):
    __tablename__ = "weekly_schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False, index=True)
    start = Column(Date, nullable=False, index=True) #inicio del cronograma
    end = Column(Date, nullable=False, index=True) #final del cronograma, normalmente deberia ser de solo una semana el cronograma, pero lo dejo asi por si lo quieren modificar
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    is_current = Column(Boolean, default=False, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="company_schedules")
    
class ScheduleTasks(base):
    __tablename__ = "schedule_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    weekly_schedule_id = Column(Integer, ForeignKey("weekly_schedules.id"), nullable=False, index=True)
    day_of_week = Column(String, nullable=False)
    activity = Column(String, nullable=False)
    order_position = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("schedule_categories.id"), nullable=True)
    category = relationship("ScheduleCategory", back_populates="tasks")
    
class WeeklyMilestones(base):
    __tablename__ = "weekly_milestones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    weekly_schedule_id = Column(Integer, ForeignKey("weekly_schedules.id"), nullable=False, index=True)
    description = Column(String, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    
class ScheduleCategory(base):
    __tablename__ = "schedule_categories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    color = Column(String(7), nullable=False)
    tasks = relationship("ScheduleTasks", back_populates="category")