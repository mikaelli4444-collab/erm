from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from core.dependencies import templates, CreateSession
from users.users_model import User
from payments.payments_models import Plans
from core.security import verify_admin
from admin.admin_services import create_plan, delete_plan_abacatepay
from utilities.limiter.limiter import limiter

admin_router = APIRouter(prefix="/admin", tags=["admin"], include_in_schema=False)

@admin_router.post("/create-plan")
@limiter.limit("5/minute")
def create_plan_route(request: Request, payload: dict, session: Session = Depends(CreateSession), user: User = Depends(verify_admin)):
    return create_plan(user, name=payload["name"], amount=payload["amount"], frequency=payload["frequency"], session=session)

@admin_router.delete("/delete-plan/{plan_id}")
def delete_plan_route(plan_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_admin)):

    plan = session.query(Plans).filter(Plans.id == plan_id).first()
    
    if not plan:
        raise HTTPException(404, "Plan no encontrado")

    delete_plan_abacatepay(plan.external_id, user)

    session.delete(plan)
    session.commit()

    return {"status": "deleted"}

#VIEWS

@admin_router.get("/plans")
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