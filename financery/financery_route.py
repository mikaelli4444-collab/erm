from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates 
from core.security import verify_token 
from users.users_model import User
from financery.financery_services import add_sell
from datetime import datetime


financery_router = APIRouter(prefix="/financery", tags=["financery"])

# KPI, son indicadores que miden si un equipo o empresa esta alcanzando sus objetivos
@financery_router.post("/")
def add_sell(delivery: datetime, client_name: str = Form(...), carpenter_id: int = Form(...), status: str = Form(...), income: float = Form(...), expenses: float = Form(...), type: str = Form(...), user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    add_sell(delivery, client_name, carpenter_id, status, income, expenses, type, user, session)
    return RedirectResponse(url="/financery/dashboard", status_code=303)