from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from users.users_model import User
from financery.financery_models import Sells
from financery.financery_schema import SellsSchema

def add_sell(data: SellsSchema, user: User, session: Session):
    
    buscar_carpintero = session.query(User).filter(User.id == data.carpenter_id, User.company_id == user.company_id).one_or_none()
    
    if not buscar_carpintero:
        return None
    
    new_sell = Sells(
        user_id = user.id,
        company_id = user.company_id,
        client_name = data.client_name,
        income = data.income,
        expenses = data.expenses,
        status = data.status,
        delivery = data.delivery,
        carpenter_id = buscar_carpintero.id
    )
    
    session.add(new_sell)
    session.commit()
    session.refresh(new_sell)
    
    return new_sell
    
