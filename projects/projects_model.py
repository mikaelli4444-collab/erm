from sqlalchemy import Integer, String, Column, ForeignKey, Boolean, DateTime, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from core.database import base
from datetime import date, datetime, timezone
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
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    description = Column(String, nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="company_projects")
    active = Column(Boolean, default=False, nullable=False, index=True) #esto es para decir si el proyecto ya se esta ejecutando en la fabrica o no
    address = Column(String, nullable=True, index=True) #direccion del cliente
    photos = relationship("ProjectsPhotos", back_populates="project", cascade="all, delete-orphan")
    pdfs = relationship("ProjectsPDFs", back_populates="project", cascade="all, delete-orphan")
    comments = relationship("Comments", back_populates="project", cascade="all, delete-orphan")
    
class ProjectsPhotos(base):
    __tablename__ = 'projects_photos'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    photo_path = Column(String, index=True, nullable=False)
    project = relationship("Projects", back_populates="photos")
    
class ProjectsPDFs(base):
    __tablename__ = 'projects_pdfs'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    pdf_path = Column(String, index=True, nullable=False)
    project = relationship("Projects", back_populates="pdfs")
    
class Comments(base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    
    
    project = relationship("Projects", back_populates="comments")
    author = relationship("User", back_populates="user_comments")
    company = relationship("Company", back_populates="company_comments")
    
class SharedProjects(base):
    __tablename__ = 'shared_projects'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    token = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    expired_at = Column(DateTime, nullable=True)