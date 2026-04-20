from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates
from core.security import verify_token
from users.users_model import User
from projects.projects_services import create_project, add_photo, add_pdf, show_projects
from projects.projects_schema import CreateProject
from utilities.storage.storage_service import StorageService

projects_router = APIRouter(prefix="/projects", tags=["prj"])

@projects_router.post("/dashboard")
def show_projects(session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    show_projects(session, user)
    return RedirectResponse(url="/projects/dashboard", status_code=303)
    

@projects_router.post("/add")
def create_new_project(user: User = Depends(verify_token), session: Session = Depends(CreateSession), data: CreateProject = Depends()):
    new_project = create_project(user, session, data)
    add_photo(project_id=new_project.id, file=data.photo, session=session, storage=StorageService())
    add_pdf(project_id=new_project.id, file=data.pdf, session=session, storage=StorageService())
    return RedirectResponse(url=f"/projects/add/{new_project.id}", status_code=303)

# VIEWS

@projects_router.get("/dashboard")
def show_projects_view(request: Request, user: User = Depends(verify_token)):
    return templates.TemplateResponse(
        "projects/projects_dashboard.html",
        {
            "request": request,
            "user": user,
        }
    )

@projects_router.get("/add")
def create_project_view(request: Request):
    return templates.TemplateResponse(
        "projects/projects_add.html",
        {
            "request": request,
        })