from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload, joinedload
from users.users_model import User
from projects.projects_model import Projects, ProjectsPhotos, ProjectsPDFs
from core.config.config_loader import RAW_CONFIG
from utilities.storage.storage_service import StorageService
from datetime import date

def map_user(user): #esta funcion es para transformar los datos de un objeto ORM a un dict y que toda la app lo entienda
    return {
    "id": user.id,
    "username": user.username,
    "fullname": user.fullname,
    "role": user.role
    }


def create_project(user: User, session: Session, name: str, carpenter_id: int, client_name: str, delivery: date, description: str, address: str):
    new_project = Projects(
        name=name,
        carpenter_id=carpenter_id,
        client_name=client_name,
        delivery=delivery,
        description=description,
        address=address,
        company_id=user.company_id
    )
    

    usuario = session.get(User, carpenter_id)
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Carpenter not found")
    
    if usuario.company_id != user.company_id:
        raise HTTPException(status_code=400, detail="Carpenter does not belong to the same company")
    
    role = usuario.role
    
    if role not in ["carpenter", "admin"]:
        raise HTTPException(status_code=400, detail="User is not a carpenter or admin")
    
    
    try:
        session.add(new_project)
        session.commit()
        session.refresh(new_project)
        
    except Exception as e:
        session.rollback()
        print(e)
        raise HTTPException(status_code=500, detail="Error creating project")
    
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
    
def tranform_content(projects):
    return [
        {
            "id": project.id,
            "name": project.name,
            "carpenter": map_user(project.carpenter),
            "client_name": project.client_name,
            "delivery": project.delivery,
            "status": project.status.value,
            "description": project.description,
            "address": project.address,
            "photos": [RAW_CONFIG.storage.media_base_url + "/" + photo.photo_path for photo in project.photos],
            "pdfs": [RAW_CONFIG.storage.media_base_url + "/" + pdf.pdf_path for pdf in project.pdfs] #aqui estoy creando un link agarrando la url de mi storage y juntandola con la ruta del archivo que quiero
        }
        for project in projects
    ]

def show_projects(session: Session, user: User):
    projects = session.query(Projects).filter(Projects.company_id == user.company_id).options(selectinload(Projects.photos), selectinload(Projects.pdfs), joinedload(Projects.carpenter)).all()
    
    transformed_projects = tranform_content(projects)
        
    return transformed_projects

def search_users(name: str, user: User, session: Session):
    return session.query(User).filter((User.company_id == user.company_id), User.username.ilike(f"%{name}%") | (User.fullname.ilike(f"%{name}%"))).all()