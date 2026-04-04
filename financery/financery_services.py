from fastapi import HTTPException
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import date
from users.users_model import User
from financery.financery_models import Sells, FinancialTransaction, Debt, Payment, Receivable
from financery.financery_schema import SellsSchema, FinancialTransactionSchema, DebtCreateSchema, PaymentCreate, ReceivableCreate
from notification.notification_services import create_notification, show_notifications, manager

def notify_invoice_due_date(user_id: int, company_id: int, message: dict, session: Session): #vencimiento de la factura
    create_notification(user_id, company_id, message, session)
    
    
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

def add_installments(user: User, session: Session, operation_num: int, debt_data: Debt, payment_schema: PaymentCreate):
    
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
        add_installments(user, session, new_debt.number_of_installments, new_debt, PaymentCreate(
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
        
def pending_debts(user: User, session: Session):
    
    pending_debts = session.query(Payment).filter(Payment.company_id == user.company_id, Payment.status == "pending").all()
    
    owner_id = session.query(User.id).filter(User.company_id == user.company_id, User.role == "owner").scalar()
     
    today = date.today()
     
    for debt in pending_debts:
        if debt.due_date < date.today():
            debt.status = "overdue"
            session.commit()    
            
        elif 0 <= (debt.due_date - today).days <= 5 and debt.status == 'pending' and debt.notification == False:
            message = {
                        "type": "invoice_due_date",
                        "data": {"message": "Your invoice is due in 5 days"}
                    }

            debt.notification = True
                
            notify_invoice_due_date(owner_id, user.company_id, message, session)
        
    session.commit()
    
def to_receive(user: User, session: Session, data: ReceivableCreate):
    
    owner_id = session.query(User.id).filter(User.company_id == user.company_id, User.role == "owner").scalar()
    
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
    
    to_receive_notify = session.query(Receivable).filter(Receivable.id == to_receive_orm.id).first()
    
    if to_receive_orm.due_date >= date.today() and to_receive_orm.due_date <= date.today() + relativedelta(days=5) and to_receive_notify.notification == False:
            message = {
                            "type": "invoice_due_date",
                            "data": {"message": f"Payment of receivable {to_receive_orm.payer_name} is due in 5 days"}
                        }
            
            to_receive_notify.notification = True
            
            notify_invoice_due_date(owner_id, user.company_id, message, session)
            session.commit()
    
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
        
def _month_start_end(reference_date: date):
    start = reference_date.replace(day=1)
    end = start + relativedelta(months=1)
    return start, end

def _calculate_percentage(value: Decimal, total: Decimal) -> float:
    if total == 0:
        return 0.0
    return round(float((value / total) * Decimal("100")), 2)

def _monthly_sales_counts(user: User, session: Session, start: date, end: date):
    total_days = (end - start).days
    labels = [str((start + relativedelta(days=i)).day) for i in range(total_days)]

    counts_query = session.query(
        FinancialTransaction.date,
        func.count(FinancialTransaction.id)).filter(
        FinancialTransaction.company_id == user.company_id,
        FinancialTransaction.type == "income",
        FinancialTransaction.category == "sale",
        FinancialTransaction.date >= start,
        FinancialTransaction.date < end).group_by(FinancialTransaction.date).all()

    counts_map = {row[0]: row[1] for row in counts_query}
    values = [counts_map.get(start + relativedelta(days=i), 0) for i in range(total_days)]
    return labels, values

def financial_transaction_charts(user: User, session: Session):
    today = date.today()
    current_start, current_end = _month_start_end(today)
    prev_start = current_start - relativedelta(months=1)
    prev_end = current_start

    current_labels, current_values = _monthly_sales_counts(user, session, current_start, current_end)
    prev_labels, prev_values = _monthly_sales_counts(user, session, prev_start, prev_end)

    month_transactions = session.query(
        func.sum(case((FinancialTransaction.type == 'income', FinancialTransaction.amount), else_=0)),
        func.sum(case((FinancialTransaction.type == 'expense', FinancialTransaction.amount), else_=0))
    ).filter(
        FinancialTransaction.date >= current_start,
        FinancialTransaction.date < current_end,
        FinancialTransaction.company_id == user.company_id
    ).first()

    total_income_amount = month_transactions[0] or Decimal("0")
    total_expenses_amount = month_transactions[1] or Decimal("0")
    total_profit = total_income_amount - total_expenses_amount
    pie_total = total_income_amount + total_expenses_amount

    return {
        "line_chart": {
            "current_month": {
                "month": current_start.strftime("%B %Y"),
                "days": current_labels,
                "sales_count": current_values,
                "total_sales": sum(current_values)
            },
            "previous_month": {
                "month": prev_start.strftime("%B %Y"),
                "days": prev_labels,
                "sales_count": prev_values,
                "total_sales": sum(prev_values)
            }
        },
        "pie_chart": {
            "income": {
                "value": total_income_amount,
                "percentage": _calculate_percentage(total_income_amount, pie_total)
            },
            "expense": {
                "value": total_expenses_amount,
                "percentage": _calculate_percentage(total_expenses_amount, pie_total)
            },
            "profit": {
                "value": total_profit,
                "percentage": _calculate_percentage(total_profit, total_income_amount) if total_income_amount != 0 else 0.0
            }
        }
    }

def get_pending_debts(user: User, session: Session):
    return session.query(Payment).filter(
        Payment.company_id == user.company_id,
        Payment.status == "pending"
    ).all()

def get_pending_receivables(user: User, session: Session):
    return session.query(Receivable).filter(
        Receivable.company_id == user.company_id
    ).all()

def _month_start_end(reference_date: date):
    start = reference_date.replace(day=1)
    end = start + relativedelta(months=1)
    return start, end

def _calculate_percentage(value: Decimal, total: Decimal) -> float:
    if total == 0:
        return 0.0
    return round(float((value / total) * Decimal("100")), 2)

def _monthly_sales_counts(user: User, session: Session, start: date, end: date):
    total_days = (end - start).days
    labels = [str((start + relativedelta(days=i)).day) for i in range(total_days)]

    counts_query = session.query(
        FinancialTransaction.date,
        func.count(FinancialTransaction.id)
    ).filter(
        FinancialTransaction.company_id == user.company_id,
        FinancialTransaction.type == "income",
        FinancialTransaction.category == "sale",
        FinancialTransaction.date >= start,
        FinancialTransaction.date < end
    ).group_by(FinancialTransaction.date).all()

    counts_map = {row[0]: row[1] for row in counts_query}
    values = [counts_map.get(start + relativedelta(days=i), 0) for i in range(total_days)]
    return labels, values

def financial_transaction_charts(user: User, session: Session):
    today = date.today()
    current_start, current_end = _month_start_end(today)
    prev_start = current_start - relativedelta(months=1)
    prev_end = current_start

    current_labels, current_values = _monthly_sales_counts(user, session, current_start, current_end)
    prev_labels, prev_values = _monthly_sales_counts(user, session, prev_start, prev_end)

    month_transactions = session.query(
        func.sum(case((FinancialTransaction.type == 'income', FinancialTransaction.amount), else_=0)),
        func.sum(case((FinancialTransaction.type == 'expense', FinancialTransaction.amount), else_=0))
    ).filter(
        FinancialTransaction.date >= current_start,
        FinancialTransaction.date < current_end,
        FinancialTransaction.company_id == user.company_id
    ).first()

    total_income_amount = month_transactions[0] or Decimal("0")
    total_expenses_amount = month_transactions[1] or Decimal("0")
    total_profit = total_income_amount - total_expenses_amount
    pie_total = total_income_amount + total_expenses_amount

    return {
        "line_chart": {
            "current_month": {
                "month": current_start.strftime("%B %Y"),
                "days": current_labels,
                "sales_count": current_values,
                "total_sales": sum(current_values)
            },
            "previous_month": {
                "month": prev_start.strftime("%B %Y"),
                "days": prev_labels,
                "sales_count": prev_values,
                "total_sales": sum(prev_values)
            }
        },
        "pie_chart": {
            "income": {
                "value": total_income_amount,
                "percentage": _calculate_percentage(total_income_amount, pie_total)
            },
            "expense": {
                "value": total_expenses_amount,
                "percentage": _calculate_percentage(total_expenses_amount, pie_total)
            },
            "profit": {
                "value": total_profit,
                "percentage": _calculate_percentage(total_profit, pie_total)
            }
        }
    }

def _parse_date(value):
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    return None


def add_installments(user: User, session: Session, operation_num: int, debt_data: Debt, payment_schema: PaymentCreate):
    if not debt_data:
        raise HTTPException(status_code=400, detail="Debt data is required")

    if operation_num <= 0:
        raise HTTPException(status_code=400, detail="Installments must be a positive integer")

    installment_amount = (Decimal(debt_data.amount) / operation_num).quantize(Decimal("0.01")) if debt_data.amount else Decimal("0.00")
    installments_list = []

    for i in range(operation_num):
        due_date = payment_schema.due_date + relativedelta(months=i)
        installment = Payment(
            user_id=user.id,
            company_id=user.company_id,
            debt_id=debt_data.id if hasattr(Payment, "debt_id") else None,
            amount=installment_amount,
            due_date=due_date,
            status="pending",
            installment_number=i + 1,
            description=getattr(payment_schema, "description", None)
        )
        installments_list.append(installment)

    session.add_all(installments_list)
    return installments_list


def add_debts(user: User, session: Session, data: DebtCreateSchema):
    creditor_name = getattr(data, "creditor_name", getattr(data, "supplier_name", None))
    debt_kwargs = {
        "user_id": user.id,
        "company_id": user.company_id,
        "amount": data.amount,
        "installments": data.installments,
        "due_date": data.due_date,
        "description": getattr(data, "description", None),
        "status": getattr(data, "status", "pending")
    }

    if creditor_name:
        if hasattr(Debt, "creditor_name"):
            debt_kwargs["creditor_name"] = creditor_name
        else:
            debt_kwargs["supplier_name"] = creditor_name

    debt = Debt(**debt_kwargs)
    session.add(debt)
    session.flush()

    payment_schema = PaymentCreate(
        amount=data.amount,
        due_date=data.due_date,
        description=getattr(data, "description", None)
    )

    add_installments(user, session, data.installments, debt, payment_schema)
    session.commit()
    return debt


def pay_debt(user: User, session: Session, payment_id: int):
    payment = session.query(Payment).filter(
        Payment.id == payment_id,
        Payment.company_id == user.company_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Pending payment not found")

    payment.status = "paid"
    if hasattr(payment, "paid_date"):
        payment.paid_date = date.today()

    session.commit()
    return payment


def pending_debts(user: User, session: Session):
    return get_pending_debts(user, session)


def to_receive(user: User, session: Session, data: ReceivableCreate):
    receivable_kwargs = {
        "user_id": user.id,
        "company_id": user.company_id,
        "amount": data.amount,
        "installments": data.installments,
        "due_date": data.due_date,
        "description": getattr(data, "description", None),
        "status": getattr(data, "status", "pending")
    }

    client_name = getattr(data, "client_name", None)
    if client_name:
        receivable_kwargs["client_name"] = client_name

    receivable = Receivable(**receivable_kwargs)
    session.add(receivable)
    session.commit()
    return receivable


def get_pending_debts(user: User, session: Session):
    return session.query(Payment).filter(
        Payment.company_id == user.company_id,
        Payment.status == "pending"
    ).order_by(Payment.due_date).all()


def get_pending_receivables(user: User, session: Session):
    return session.query(Receivable).filter(
        Receivable.company_id == user.company_id,
        Receivable.paid_at.is_(None)
    ).order_by(Receivable.due_date).all()


def pay_receivable(user: User, session: Session, receivable_id: int):
    receivable = session.query(Receivable).filter(
        Receivable.id == receivable_id,
        Receivable.company_id == user.company_id
    ).first()

    if not receivable:
        raise HTTPException(status_code=404, detail="Receivable not found")

    receivable.paid_at = date.today()
    session.commit()
    return receivable

def delete_payment(user: User, session: Session, payment_id: int):
    payment = session.query(Payment).filter(
        Payment.id == payment_id,
        Payment.company_id == user.company_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Pending payment not found")

    session.delete(payment)
    session.commit()
    return payment


def delete_receivable(user: User, session: Session, receivable_id: int):
    receivable = session.query(Receivable).filter(
        Receivable.id == receivable_id,
        Receivable.company_id == user.company_id
    ).first()

    if not receivable:
        raise HTTPException(status_code=404, detail="Receivable not found")

    session.delete(receivable)
    session.commit()
    return receivable


def edit_payment(user: User, session: Session, payment_id: int, data: dict):
    payment = session.query(Payment).filter(
        Payment.id == payment_id,
        Payment.company_id == user.company_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Pending payment not found")

    if "amount" in data:
        payment.amount = Decimal(str(data["amount"]))
    if "due_date" in data:
        parsed = _parse_date(data["due_date"])
        if parsed:
            payment.due_date = parsed
    if "status" in data:
        payment.status = data["status"]
    if "installment_number" in data:
        payment.installment_number = data["installment_number"]
    if "description" in data:
        payment.description = data["description"]

    session.commit()
    return payment


def edit_receivable(user: User, session: Session, receivable_id: int, data: dict):
    receivable = session.query(Receivable).filter(
        Receivable.id == receivable_id,
        Receivable.company_id == user.company_id
    ).first()

    if not receivable:
        raise HTTPException(status_code=404, detail="Receivable not found")

    if "amount" in data:
        receivable.amount = Decimal(str(data["amount"]))
    if "due_date" in data:
        parsed = _parse_date(data["due_date"])
        if parsed:
            receivable.due_date = parsed
    if "status" in data:
        receivable.status = data["status"]
    if "installments" in data:
        receivable.installments = data["installments"]
    if "description" in data:
        receivable.description = data["description"]
    if "client_name" in data:
        receivable.client_name = data["client_name"]

    session.commit()
    return receivable


def financial_transaction_charts(user: User, session: Session):
    today = date.today()
    current_start, current_end = _month_start_end(today)
    prev_start = current_start - relativedelta(months=1)
    prev_end = current_start

    current_labels, current_values = _monthly_sales_counts(user, session, current_start, current_end)
    prev_labels, prev_values = _monthly_sales_counts(user, session, prev_start, prev_end)

    month_transactions = session.query(
        func.sum(case((FinancialTransaction.type == 'income', FinancialTransaction.amount), else_=0)),
        func.sum(case((FinancialTransaction.type == 'expense', FinancialTransaction.amount), else_=0))
    ).filter(
        FinancialTransaction.date >= current_start,
        FinancialTransaction.date < current_end,
        FinancialTransaction.company_id == user.company_id
    ).first()

    total_income_amount = month_transactions[0] or Decimal("0")
    total_expenses_amount = month_transactions[1] or Decimal("0")
    total_profit = total_income_amount - total_expenses_amount
    pie_total = total_income_amount + total_expenses_amount

    return {
        "line_chart": {
            "current_month": {
                "month": current_start.strftime("%B %Y"),
                "days": current_labels,
                "sales_count": current_values,
                "total_sales": sum(current_values)
            },
            "previous_month": {
                "month": prev_start.strftime("%B %Y"),
                "days": prev_labels,
                "sales_count": prev_values,
                "total_sales": sum(prev_values)
            }
        },
        "pie_chart": {
            "income": {
                "value": float(total_income_amount),
                "percentage": _calculate_percentage(total_income_amount, pie_total)
            },
            "expense": {
                "value": float(total_expenses_amount),
                "percentage": _calculate_percentage(total_expenses_amount, pie_total)
            },
            "profit": {
                "value": float(total_profit),
                "percentage": _calculate_percentage(total_profit, pie_total)
            }
        }
    }