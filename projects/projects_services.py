from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import date
from users.users_model import User
from projects.projects_model import Projects, ProjectsPhotos, ProjectsPDFs
from core.config.config_loader import RAW_CONFIG
from utilities.storage.storage_service import StorageService

def map_user(user):
    return {
    "id": user.id,
    "image_url": RAW_CONFIG.storage.media_base_url + "/" + user.image_path
    }


def create_project(user: User, session: Session, name: str, carpenter_id: int, client_name: str, delivery: str, description: str, address: str):
    new_project = Projects(
        name=name,
        carpenter_id=carpenter_id,
        client_name=client_name,
        delivery=delivery,
        description=description,
        address=address,
        company_id=user.company_id
    )
    session.add(new_project)
    session.commit()
    session.refresh(new_project)
    return new_project


def add_photo(project_id: int, file, session: Session, storage: StorageService):
    
    project = session.get(Projects, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        path = storage.upload_file(file)
        
    except Exception:
        raise HTTPException(500, "Error uploading file")
    
    photo = ProjectsPhotos(
        project_id=project_id,
        photo_path=path
    )
    
    try:
        session.add(photo)
        session.commit()
        session.refresh(photo)
        
        return photo
        
    except Exception:
        session.rollback()
        
        try:
            storage.delete_file(path)
        
        except:
            pass 
        
        raise HTTPException(status_code=500, detail="Error saving photo to database")

def add_pdf(project_id: int, file, session: Session, storage: StorageService):

    project = session.get(Projects, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        path = storage.upload_file(file)
    except Exception:
        raise HTTPException(500, "Error uploading file")
    
    pdf = ProjectsPDFs(
        project_id=project_id,
        pdf_path=path
    )   
    
    try:
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        return pdf
    
    except Exception as e:
        session.rollback()
        
        try:
            storage.delete_file(path)
        
        except:
            pass 
        
        raise HTTPException(status_code=500, detail="Error saving pdf to database")

def show_projects(session: Session, user: User):
    projects = session.query(Projects).filter(Projects.company_id == user.company_id).all()
    return projects

def search_users(name: str, session: Session):
    return session.query(User).filter(User.name.ilike(f"%{name}%")).all()
