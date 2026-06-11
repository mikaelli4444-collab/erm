from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from core.dependencies import templates, CreateSession
from users.users_model import User
from core.security import verify_admin
from admin.admin_services import create_plan
from utilities.limiter.limiter import limiter

admin_router = APIRouter(prefix="/admin", tags=["admin"], include_in_schema=False)

@admin_router.post("/create-plan")
@limiter.limit("5/minute")
def create_plan_route(request: Request, payload: dict, session: Session = Depends(CreateSession), user: User = Depends(verify_admin)):
    return create_plan(user, name=payload["name"], amount=payload["amount"], frequency=payload["frequency"], session=session)

#VIEWS

@admin_router.get("/create-plan")
@limiter.limit("5/minute")
def create_plan_page(request: Request, user: User = Depends(verify_admin), session: Session = Depends(CreateSession)):
    
    if user.role != "admin":
        return templates.TemplateResponse("responses/404.html", {
            "request": request
        })
    
    else:
        return templates.TemplateResponse("plans/create_plans.html", {
            "request": request,
            "user": user
        })