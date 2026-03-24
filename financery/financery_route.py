from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from production.production_model import Production
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates 
from core.security import verify_token 
from production.production_schema import create_production
from users.users_model import User


financery_router = APIRouter(prefix="/financery", tags=["financery"])

# KPI, son indicadores que miden si un equipo o empresa esta alcanzando sus objetivos
@financery_router.post("/")
