from sqlalchemy import Integer, String, Column, DateTime, ForeignKey, DECIMAL, Boolean, Date, Computed, Enum as SQLEnum
from sqlalchemy.orm import relationship
from core.database import base
from datetime import datetime, date
from core.enum.enum import StatusEnum, DebtStatusEnum, TransactionTypeEnum, TransactionCategoryEnum, ReceivablesStatusEnum
    
class Sells(base):
    __tablename__ = "sells"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id")) #quien registro la venta o quien fue el responsable de la venta
    user = relationship("User", foreign_keys=[user_id], back_populates="sells")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="company_sells")
    client_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    client_name =  Column(String, nullable=True, index=True)
    installments = Column(Integer, nullable=False, index=True)
    income = Column(DECIMAL, nullable=False, index=True) #Ingresos
    expenses = Column(DECIMAL, nullable=False, index=True) #Egresos
    profit = Column(DECIMAL, Computed("income - expenses"), index=True)
    status = Column(SQLEnum(StatusEnum), nullable=False)
    date_sell = Column(Date, default=date.today, nullable=False) #definir fecha manualmente
    delivery = Column(Date, nullable=False) #definir fecha manualmente
    carpenter_id = Column(Integer, ForeignKey("users.id"))
    carpenter = relationship("User", foreign_keys=[carpenter_id], back_populates="in_charge")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Debt(base): #Deudas
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amount = Column(DECIMAL, nullable=False, index=True) #cantidad a pagar TOTAL
    creditor = Column(String, nullable=False, index=True) #acreedor
    number_of_installments = Column(Integer, default=1) #aqui tengo el numero de cuotas, si tiene un valor > 1 entonces pagarla todos los meses el mismo dia que se indico en due_date
    description = Column(String)
    payments = relationship("Payment", back_populates="debt", cascade="all, delete-orphan")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="company_debts")
    status = Column(SQLEnum(DebtStatusEnum), nullable=False, default="pending")#pending, paid, cancelled, overdue (overdue = atrasado), 
    notification = Column(Boolean, nullable=False, default=False)
    
class Payment(base): #cuotas
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    debt_id = Column(Integer, ForeignKey("debts.id", ondelete="CASCADE"))
    debt = relationship("Debt", back_populates="payments")
    amount = Column(DECIMAL, nullable=False, index=True) #cantidad a pagar CUOTAS
    due_date = Column(Date, index=True) #todos los meses el mismo dia por la cantidad de meses que se indico
    paid = Column(Boolean, nullable=False, default=False)
    paid_at = Column(Date, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="company_payments")
    status = Column(SQLEnum(DebtStatusEnum), nullable=False, default="pending")#pending, paid, cancelled, overdue (overdue = atrasado)
    installment_number = Column(Integer, nullable=True)
    total_installments = Column(Integer, nullable=False, default=1)
    
class Receivable(base): #para recibir
    __tablename__ = "receivables"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    amount = Column(DECIMAL, nullable=False, index=True)
    due_date = Column(Date, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    receiver = relationship("User", back_populates="to_recebe")
    payer_id = Column(Integer, ForeignKey("contacts.id"), nullable=True, index=True) #pagador
    payer = relationship("Contacts", back_populates="payments")
    payer_name = Column(String, nullable=True, index=True)
    description = Column(String, nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="company_receivable")
    status = Column(SQLEnum(ReceivablesStatusEnum), default=ReceivablesStatusEnum.pending)
    paid_at = Column(Date, nullable=True)
    notification = Column(Boolean, nullable=False, default=False)
    
class FinancialTransaction(base):
    __tablename__ = "transactions" #METER SOLO LAS TRANSACCIONES QUE REALMENTE SE EFECTUARON, VERIFICAR ESO EN BACK
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="company_financial_transactions")
    type = Column(SQLEnum(TransactionTypeEnum), nullable=False)
    amount = Column(DECIMAL, nullable=False, index=True)
    date = Column(Date, default=date.today, nullable=False, index=True)
    category = Column(SQLEnum(TransactionCategoryEnum), nullable=False)
    description = Column(String, nullable=True, index=True)
    reference_id = Column(Integer, index=True)
    is_variable = Column(Boolean, default=False)