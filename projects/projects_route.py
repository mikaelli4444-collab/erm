from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from users.users_model import User
from projects.projects_services import create_project, add_photo, add_pdf
from projects.projects_schema import CreateProject
from utilities.storage.storage_service import StorageService

projects_router = APIRouter(prefix="/projects", tags=["prj"])

@projects_router.post("/add")
def create_new_project(user: User = Depends(), session: Session = Depends(CreateSession), data: CreateProject = Depends()):
    new_project = create_project(user, session, data)
    return RedirectResponse(url=f"/inv/projects/{new_project.id}", status_code=303)