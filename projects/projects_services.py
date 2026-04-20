from fastapi import HTTPException
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import date
from users.users_model import User
from projects.projects_schema import CreateProject
from projects.projects_model import Projects
from core.config.config_loader import RAW_CONFIG
from utilities.storage.storage_service import StorageService

def map_user(user):
    return {
    "id": user.id,
    "image_url": RAW_CONFIG.storage.media_base_url + "/" + user.image_path
    }


def create_project(user: User, session: Session, data: CreateProject):
    
    new_project = Projects(
        name=data.name,
        carpenter=data.carpenter,
        client_name=data.client_name,
        delivery=data.delivery,
        description=data.description,
        address=data.address,
        company_id=user.company_id
    )
    session.add(new_project)
    session.commit()
    session.refresh(new_project)
    return new_project


def add_photo(project_id: int, file, session: Session, storage: StorageService):
    
    project = session.query(Projects).filter(Projects.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    old_path = project.photo_path

    new_path = storage.upload_file(file)

    project.photo_path = new_path

    session.commit()
    session.refresh(project)

    if old_path:
        try:
            storage.delete_file(old_path)
        except Exception:
            pass

    return project


def add_pdf(project_id: int, file, session: Session, storage: StorageService):
    
    project = session.query(Projects).filter(Projects.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    old_path = project.pdf_path

    new_path = storage.upload_file(file)

    project.pdf_path = new_path

    session.commit()
    session.refresh(project)

    if old_path:
        try:
            storage.delete_file(old_path)
        except Exception:
            pass

    return project

def show_projects(session: Session, user: User):
    projects = session.query(Projects).filter(Projects.company_id == user.company_id).all()
    return projects