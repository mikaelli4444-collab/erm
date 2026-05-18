from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from projects.projects_model import Projects
from sqlalchemy import or_
from typing import List
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates
from core.security import verify_token
from users.users_model import User
from projects.projects_services import create_project, add_photo, add_pdf, show_projects, generate_project_share_link, get_shared_project_by_token, delete_link
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
        
    return RedirectResponse(url=f"/projects/dashboard", status_code=303)

@projects_router.post("/create_link/{project_id}")
def create_link(project_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    project = session.get(Projects, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.company_id != user.company_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this project")
    
    link = generate_project_share_link(project_id, session)
    token = link["token"]
    
    return {
        "share_link": link, 
        "token": token
        }

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
def search_users_route(username: str, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    users = session.query(User).filter((User.company_id == user.company_id), User.username.ilike(f"%{username}%") | (User.fullname.ilike(f"%{username}%"))).all()

    return [
        {"id": user.id, "name": user.username}
        for user in users
    ]
            
@projects_router.get("/public/projects/client")
def shared_projects_client_view(request: Request, token: str, session: Session = Depends(CreateSession)):
    shared_project = get_shared_project_by_token(token, session)
    
    if not shared_project:
        raise HTTPException(status_code=404, detail="Shared project not found")
    
    return templates.TemplateResponse(
        "projects/client_exp.html",
        {
            "request": request,
            "project": {
                "name": shared_project.name,
                "client_name": shared_project.client_name,
                "delivery": shared_project.delivery,
                "description": shared_project.description,
                "address": shared_project.address,
                "carpenter": shared_project.carpenter.fullname,
                "photos": [RAW_CONFIG.storage.media_base_url + "/" + photo.photo_path for photo in shared_project.photos],
                "pdfs": [RAW_CONFIG.storage.media_base_url + "/" + pdf.pdf_path for pdf in shared_project.pdfs],
                "company_name": shared_project.company.name,
                #"company_logo": RAW_CONFIG.storage.media_base_url + "/" + project.company.logo_path if project.company.logo_path else None,
                "created_at": shared_project.created_at,
                "comments": [
                    {
                        "author": comment.author.fullname,
                        "date": comment.created_at,
                        "text": comment.text
                    }
                    for comment in shared_project.comments]
            },
            
            # "comments": [
            #     {
            #         "author": comment.author.fullname,
            #         "date": comment.created_at,
            #         "text": comment.text
            #     }
            #     for comment in shared_project.comments
            #     ]
            }
        )
    
@projects_router.get("/{project_id}")
def show_projects_details(request: Request, project_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    project = session.get(Projects, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.company_id != user.company_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this project")
    
    return templates.TemplateResponse(
        "projects/projects_details.html",
        {
            "request": request,
            
            "project": {
                "id": project.id,        
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
                #"company_logo": RAW_CONFIG.storage.media_base_url + "/" + project.company.logo_path if project.company.logo_path else None,
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