from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from users.users_model import User
from financery.financery_models import Sells

def add_sell(delivery: datetime, client_name: str, carpenter_id: int, status: str, income: float, expenses: float, type: str, user: User, session: Session):
    
    new_sell = Sells(
        user_id = user,
        company_id = user.company_id,
        type = type,
        income = income,
        expenses = expenses,
        client_name = client_name,
        delivery = delivery,
        carpenter_id = carpenter_id,
        status = status
    )
    
    session.add(new_sell)
    session.commit()
    session.refresh
    
    return{
        "message": "Inventory item created successfully",
        "sell": new_sell
    }