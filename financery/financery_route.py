from fastapi import APIRouter, Depends, Request, HTTPException, Body
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates
from core.security import verify_token
from users.users_model import User
from financery.financery_services import (
    add_sell,
    kdis_calculate,
    financial_transaction_charts,
    get_pending_debts,
    get_pending_receivables,
    add_debts,
    to_receive,
    pay_debt,
    pay_receivable,
    delete_payment,
    delete_receivable,
    edit_payment,
    edit_receivable,
    is_owner
)
from financery.financery_models import Sells
from financery.financery_schema import SellsSchema, DebtCreateSchema, ReceivableCreate
from datetime import date

financery_router = APIRouter(prefix="/financery", tags=["financery"])


@financery_router.post("/dashboard")
@financery_router.post("/sell")
def add_sell_endpoint(data: SellsSchema, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    is_owner = is_owner(user)
    
    if is_owner:
        add_sell(user, session, data)
        return RedirectResponse("/financery/dashboard", status_code=303)
    
    else:
        return ValueError('No Owner')


@financery_router.delete("/sell/{sell_id}")
def delete_sell_endpoint(sell_id: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    is_owner = is_owner(user)
    
    if is_owner:
        sell = session.query(Sells).filter(Sells.id == sell_id, Sells.company_id == user.company_id).first()
        if not sell:
            raise HTTPException(status_code=404, detail="Sell not found")
        session.delete(sell)
        session.commit()
        return {"message": "Sell deleted"}
    
    else:
        return ValueError('No Owner')


@financery_router.post("/dashboard/debt")
def create_debt(data: DebtCreateSchema, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    is_owner = is_owner(user)
    
    if is_owner:
        add_debts(user, session, data)
        return {"message": "Debt created"}
    
    else:
        return ValueError('No Owner')


@financery_router.post("/dashboard/receivable")
def create_receivable(data: ReceivableCreate, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    is_owner = is_owner(user)
    
    if is_owner:
        to_receive(user, session, data)
        return {"message": "Receivable created"}
    
    else:
        return ValueError('No Owner')


@financery_router.post("/dashboard/payment/{payment_id}/pay")
def pay_debt_endpoint(payment_id: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    is_owner = is_owner(user)
    
    if is_owner:
        pay_debt(user, session, payment_id)
        return {"message": "Payment marked as paid"}
    
    else:
        return ValueError('No Owner')


@financery_router.post("/dashboard/receivable/{receivable_id}/pay")
def pay_receivable_endpoint(receivable_id: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    is_owner = is_owner(user)
    
    if is_owner:
        pay_receivable(user, session, receivable_id)
        return {"message": "Receivable marked as paid"}
    
    else:
        return ValueError('No Owner')


@financery_router.delete("/dashboard/payment/{payment_id}")
def delete_payment_endpoint(payment_id: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    is_owner = is_owner(user)
    
    if is_owner:
        delete_payment(user, session, payment_id)
        return {"message": "Pending payment deleted"}
    
    else:
        return ValueError('No Owner')


@financery_router.delete("/dashboard/receivable/{receivable_id}")
def delete_receivable_endpoint(receivable_id: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    is_owner = is_owner(user)
    
    if is_owner:
        delete_receivable(user, session, receivable_id)
        return {"message": "Receivable deleted"}
    
    else:
        return ValueError('No Owner')


@financery_router.put("/dashboard/payment/{payment_id}")
def edit_payment_endpoint(payment_id: int, data: dict = Body(...), user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    is_owner = is_owner(user)
    
    if is_owner:
        edit_payment(user, session, payment_id, data)
        return {"message": "Pending payment updated"}
    
    else:
        return ValueError('No Owner')


@financery_router.put("/dashboard/receivable/{receivable_id}")
def edit_receivable_endpoint(receivable_id: int, data: dict = Body(...), user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    is_owner = is_owner(user)
    
    if is_owner:
        edit_receivable(user, session, receivable_id, data)
        return {"message": "Receivable updated"}
    
    else:
        return ValueError('No Owner')

#VIEWS

@financery_router.get("/dashboard")
def show_sell(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    
    sells = session.query(Sells).filter(Sells.company_id == user.company_id).all()
    
    kdi_data = kdis_calculate(user, session)
    chart_data = financial_transaction_charts(user, session)
    pending_debts = get_pending_debts(user, session)
    receivables = get_pending_receivables(user, session)
    today = date.today()

    return templates.TemplateResponse("financery/financery_dashboard.html", {
        "request": request,
        "sells": sells,
        "kdi_data": kdi_data,
        "chart_data": chart_data,
        "pending_debts": pending_debts,
        "receivables": receivables,
        "today": today,
        "user": user
    })