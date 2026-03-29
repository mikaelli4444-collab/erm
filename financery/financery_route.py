from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates 
from core.security import verify_token 
from users.users_model import User
from financery.financery_services import add_sell
from financery.financery_models import Sells
from financery.financery_schema import SellsSchema
from datetime import datetime


financery_router = APIRouter(prefix="/financery", tags=["financery"])

# KPI, son indicadores que miden si un equipo o empresa esta alcanzando sus objetivos
@financery_router.post("/dashboard")
def add_sell_endpoint(data: SellsSchema, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    add_sell(data, user, session)
    return RedirectResponse("/financery/dashboard", status_code=303)


#VIEWS
@financery_router.get("/dashboard")
def show_sell(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    
    sells = session.query(Sells).filter(Sells.company_id == user.company_id).all()
    
    return templates.TemplateResponse("financery/financery_dashboard.html", {
        "request": request,
        "sells": sells,
        "user": user
    })
    