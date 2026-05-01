from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from core.security import verify_token
from users.users_model import User
from core.dependencies import CreateSession
from payments.payments_services import create_plan, save_plan
from sqlalchemy.orm import Session
from payments.payments_models import Plans

payments_router = APIRouter(prefix="/payment", tags=["payment"])

@payments_router.post("/create_plan")
def create_plan_post( name: str, amount: float, frequency: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):    
    if user.role == "admin":
        
        plan = session.query(Plans).filter(Plans.name == name, Plans.frequency == frequency, Plans.amount == amount).first()
    
        if plan:
            return {
                "id": plan.mp_plan_id,
                "name": plan.name,
                "amount": plan.amount,
                "frequency": plan.frequency,
            }
        
        else:
            planes = save_plan(create_plan(name, amount, frequency), name, amount, frequency, session)
            
            return {
                "id": planes.mp_plan_id,
                "name": name,
                "amount": amount,
                "frequency": frequency,
            }
    
    else:
        raise HTTPException(status_code=403, detail="No autorizado")

#VIEWS