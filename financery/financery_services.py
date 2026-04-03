from fastapi import HTTPException
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import date
from users.users_model import User
from financery.financery_models import Sells, FinancialTransaction, Debt, Payment, Receivable
from financery.financery_schema import SellsSchema, FinancialTransactionSchema, DebtCreateSchema, PaymentCreate, ReceivableCreate

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

def add_installments(operation_num, user: User, session: Session, debt_data: Debt, payment_schema: PaymentCreate):
    
    debt = debt_data
    
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    
    debt_id = debt.id
    
    installments_list = []
    
    for i in range(operation_num):

        installments = Payment(
            debt_id = debt_id,
            amount = payment_schema.amount,
            due_date = payment_schema.due_date + relativedelta(months= i + 1),
            paid = payment_schema.paid,
            status = payment_schema.status,
            company_id = user.company_id,
            installment_number = i + 1,
            total_installments = operation_num
        )
        installments_list.append(installments)
    
    session.add_all(installments_list)
    
    return installments_list

def add_sell(user: User, session: Session, data: SellsSchema):
    
    carpenter = None
    
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
    
def add_debts(user: User, session: Session, data: DebtCreateSchema):
    
    new_debt = Debt(
        company_id = user.company_id,
        amount = data.amount,
        creditor = data.creditor,
        number_of_installments = data.number_of_installments,
        description = data.description,
        status = data.status
    )
    
    session.add(new_debt)
    session.flush()
    
    if new_debt.number_of_installments > 1:
        add_installments(new_debt.number_of_installments, user, session, new_debt, PaymentCreate(
                                                                                                debt_id = new_debt.id,
                                                                                                amount = (new_debt.amount / new_debt.number_of_installments).quantize(Decimal("0.01")),
                                                                                                due_date = date.today(),
                                                                                                paid = False,
                                                                                                status = "pending"))
    else:
        installment = Payment(
            debt_id = new_debt.id,
            amount = new_debt.amount,
            due_date = date.today(),
            paid = False,
            status = "pending",
            company_id = user.company_id,
            installment_number = 1,
            total_installments = 1
        )
        session.add(installment)
        
    session.commit()
    
    return new_debt

def pay_debt(user: User, session: Session, payment_id: int):
    payment = session.query(Payment).filter(Payment.id == payment_id, Payment.company_id == user.company_id).one_or_none()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment.paid:
        raise HTTPException(status_code=400, detail="Payment already paid")
    
    payment.paid = True
    payment.status = "paid"
    
    paid_debt_schema = FinancialTransactionSchema(
        type="expense",
        category="debt_payment",
        amount=payment.amount,
        description=f"Payment of debt installment {payment.installment_number}/{payment.total_installments}",
        reference_id=payment.id,
        is_variable=False,
        date=date.today()
    )
    
    payment_data = add_new_transaction(paid_debt_schema, user)
    session.add(payment_data)
    session.commit()
        
def peding_debts(user: User, session: Session):
    
    pending_debts = session.query(Payment).filter(Payment.company_id == user.company_id, Payment.status == "pending").all()
    
    owner_id = session.query(User.id).filter(User.company_id == user.company_id, User.role == "owner").scalar()
     
    for debt in pending_debts:
        if debt.due_date < date.today():
            debt.status = "overdue"
        elif date.today() <= debt.due_date <= date.today() + relativedelta(days=5):
             # agregar la lógica para enviar notificaciones a los usuarios sobre las deudas 5 días antes de su vencimiento
            pass
    
def to_receive(user: User, session: Session, data: ReceivableCreate):
    to_receive_orm = Receivable(
        amount = data.amount,
        due_date = data.due_date,
        receiver_id = data.receiver_id,
        payer_id = data.payer_id,
        payer_name = data.payer_name,
        description = data.description,
        company_id = user.company_id
    )
    
    session.add(to_receive_orm)
    session.commit()
    
    if to_receive_orm.due_date >= date.today() and to_receive_orm.due_date <= date.today() + relativedelta(days=5):
        # agregar la lógica para enviar notificaciones a los usuarios sobre los recibibles 5 días antes de su vencimiento pero despues porque el websocket ta dificil
        pass
    
    if to_receive_orm.due_date < date.today():
        to_receive_orm.status = "overdue"
        session.commit()
        
    if to_receive_orm.status == "paid":
        paid_receivable_schema = FinancialTransactionSchema(
            type="income",
            category="receivable_payment",
            amount=to_receive_orm.amount,
            description=f"Payment received for receivable {to_receive_orm.id}",
            reference_id=to_receive_orm.id,
            is_variable=False,
            date=date.today()
        )
        
        payment_data = add_new_transaction(paid_receivable_schema, user)
        session.add(payment_data)
        session.commit()