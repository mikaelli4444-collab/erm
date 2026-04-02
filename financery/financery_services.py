from fastapi import HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import date
from users.users_model import User
from financery.financery_models import Sells, FinancialTransaction
from financery.financery_schema import SellsSchema, FinancialTransactionSchema

def add_new_transaction(data: FinancialTransactionSchema, user: User):
    
    return FinancialTransaction( 
        company_id=user.company_id,
        type=data.type,
        category=data.category,
        amount=data.amount,
        date=data.date,
        description=data.description,
        reference_id=data.reference_id,
        is_variable=data.is_variable
    )


def add_sell(user: User, session: Session, data: SellsSchema):
    
    if data.carpenter_id:
        carpenter = session.query(User).filter(User.id == data.carpenter_id, User.company_id == user.company_id).one_or_none()
    
    if not carpenter:
        raise HTTPException(status_code=404, detail="Carpenter not found")
    
    new_sell = Sells(
        user_id = user.id,
        company_id = user.company_id,
        client_name = data.client_name,
        income = data.income,
        expenses = data.expenses,
        status = data.status,
        delivery = data.delivery,
        carpenter_id = carpenter.id if carpenter else None,
        installments = data.installments
    )

    session.add(new_sell)
    session.flush()
    
    income_schema = FinancialTransactionSchema(
    type="income",
    category="sale",
    amount=data.income,
    description=f"Sell to {data.client_name}",
    reference_id=new_sell.id,
    is_variable=False
)
    
    expense_schema = FinancialTransactionSchema(
    type="expense",
    category="material",
    amount=data.expenses,
    description=f"Invested in {data.client_name}",
    reference_id=new_sell.id,
    is_variable=False
)
    
    income_data = add_new_transaction(income_schema, user)
    expense_data = add_new_transaction(expense_schema, user)
    
    session.add(income_data)
    session.add(expense_data)
    session.commit()
    
    return new_sell
    
def kdis_calculate(user: User, session: Session):
    
    today = date.today()
    
    inicio_mes = today.replace(day=1)

    if today.month == 12:
        inicio_mes_siguiente = today.replace(year=today.year + 1, month=1, day=1)
        
    else:
        inicio_mes_siguiente = today.replace(month=today.month + 1, day=1)
    
    month_transactions = session.query(func.sum(case((FinancialTransaction.type == 'income', FinancialTransaction.amount), else_=0)),
                                        func.sum(case((FinancialTransaction.type == 'expense', FinancialTransaction.amount), else_=0))).filter(
                                                                    FinancialTransaction.date >= inicio_mes,
                                                                    FinancialTransaction.date < inicio_mes_siguiente,
                                                                    FinancialTransaction.company_id == user.company_id).first()
                                        
    total_income_amount = month_transactions[0] or 0
    total_expenses_amount = month_transactions[1] or 0
    
    
    total_profit = total_income_amount - total_expenses_amount
    
    return {
        "total_income": total_income_amount,
        "total_expenses": total_expenses_amount,
        "total_profit": total_profit
    }
    
def pending_debts(user: User, session: Session):
    pass
    #1. crear deuda y agregarla a la db debts
    # 1.1 si una deuda esta parcelada (pagada en cuotas) guardar la misma deuda varias veces en la db para pagar el mismo dia pero en diferentes meses
    # 2. mostrarla con dos botones (acciones) que serian pagar y eliminar
    # 3. mostrar un recordatorio en las notificaciones 5 dias antes de vencerce la deuda
    # 4. si deuda = pagada guardar en transacciones con los datos y eliminar de debts#