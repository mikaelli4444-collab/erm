from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from projects.projects_model import Projects, ProjectsPhotos, ProjectsPDFs
from typing import List
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates
from core.security import verify_token
from users.users_model import User
from projects.projects_services import create_project, add_photo, add_pdf, show_projects, tranform_content
from utilities.storage.storage_service import StorageService
from datetime import date
from core.config.config_loader import RAW_CONFIG

projects_router = APIRouter(prefix="/projects", tags=["prj"])

@projects_router.post("/dashboard")
def show_projects_router(session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    show_projects(session, user)
    return RedirectResponse(url="/projects/dashboard", status_code=303)
    

@projects_router.post("/add")
def create_new_project(user: User = Depends(verify_token), session: Session = Depends(CreateSession), name: str = Form(...), carpenter_id: int = Form(...), client_name: str = Form(...), delivery: date = Form(...), description: str = Form(...), address: str = Form(...), photo: List[UploadFile] = File([]), pdf: List[UploadFile] = File([])):
    new_project = create_project(user, session, name, carpenter_id, client_name, delivery, description, address)
    
    storage = StorageService(RAW_CONFIG) #nota mental: aqui le estoy pasando toda la config porque el storage necesita saber el valor de variables de entorno
    
    for file in photo:
        add_photo(project_id=new_project.id, file=file, session=session, storage=storage)
    
    for file in pdf:
        add_pdf(project_id=new_project.id, file=file, session=session, storage=storage)
        
    return RedirectResponse(url=f"/projects/add/", status_code=303)

# VIEWS

@projects_router.get("/dashboard")
def show_projects_view(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    return templates.TemplateResponse(
        "projects/projects_dashboard.html",
        {
            "request": request,
            "user": user,
            "items": show_projects(session, user)
        }
    )

@projects_router.get("/add")
def create_project_view(request: Request):
    return templates.TemplateResponse(
        "projects/projects_add.html",
        {
            "request": request,
        })
    
@projects_router.get("/users/search") #esta funcion es para el autocomplete del input de carpintero en el html
def search_users_route(username: str, session: Session = Depends(CreateSession)):
    users = session.query(User)\
        .filter(User.username.ilike(f"%{username}%"))\
        .limit(10)\
        .all()

    return [
        {"id": u.id, "name": u.username}
        for u in users
    ]
    
@projects_router.get("/project/{project_id}")
def show_projects_details(request: Request, project_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    project = session.get(Projects, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.company_id != user.company_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this project")
    
    return templates.TemplateResponse(
        "projects/projects_details.html",
        {
            "project": {
                "id": project.id,
                "request": request,
                "user": user,
                "description": project.description,
                "name": project.name,
                "client_name": project.client_name,
                "delivery": project.delivery,
                "status": project.status.value,
                "address": project.address,
                "carpenter": project.carpenter.fullname,
                "photos": [RAW_CONFIG.storage.media_base_url + "/" + photo.photo_path for photo in project.photos],
                "pdfs": [RAW_CONFIG.storage.media_base_url + "/" + pdf.pdf_path for pdf in project.pdfs],
                "company_name": project.company.name,
                "company_logo": RAW_CONFIG.storage.media_base_url + "/" + project.company.logo_path if project.company.logo_path else None,
                "created_at": project.created_at,
                "comments": [
                    {
                        "author": comment.author.fullname,
                        "date": comment.created_at,
                        "text": comment.text
                    }
                    for comment in project.comments]
            }
        }
    )
            