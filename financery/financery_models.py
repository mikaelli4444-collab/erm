from sqlalchemy import Integer, String, Column, DateTime, ForeignKey, DECIMAL, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from core.database import base
from datetime import datetime

class Sells(base):
    __tablename__ = "sells"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id")) #quien registro la venta o quien fue el responsable de la venta
    user = relationship("User", foreign_keys=[user_id], back_populates="sells")
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    company = relationship("Company", back_populates="company_sells")
    type = Column(String)
    income = Column(Integer, nullable=False, index=True) #Ingresos
    expenses = Column(Integer, nullable=False, index=True) #Egresos

    @property
    def profit(self):
        return self.income - self.expenses #calcula los lucros automaticamente para no tener que hacerlo manualmente y evitar errores humanos  *LEER LA NOTA*
    
    delivery = Column(DateTime, nullable=False) #definir fecha manualmente
    carpenter_id = Column(Integer, ForeignKey("users.id"))
    carpenter = relationship("User", foreign_keys=[carpenter_id], back_populates="in_charge")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


    #EN ESE CASO EL PROFIT NO PODRA SER LLAMADO EN UNA QUERY PORQUE NO FORMA PARTE DEL SQL, FORMA PARTE DE PYTHON, PARA USARLO LO TENGO QUE LLAMAR COMO UNA PROPIEDAD NORMAL
    # sells.profit, asi puedo usarlo, calcular con el y mandarlo al front


class Debt(base): #Deudas
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amount = Column(DECIMAL, nullable=False, index=True) #cantidad a pagar TOTAL
    creditor = Column(String, nullable=False, index=True) #acreedor
    number_of_installments = Column(Integer, default=1) #aqui tengo el numero de cuotas, si tiene un valor > 1 entonces pagarla todos los meses el mismo dia que se indico en due_date
    description = Column(String)
    payments = relationship("Payment", back_populates="debt", cascade="all, delete-orphan")
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    company = relationship("Company", back_populates="company_debts")
    status = Column(String, default="pending")#pending, paid, cancelled, overdue (overdue = atrasado), 


class Payment(base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    debt_id = Column(Integer, ForeignKey("debts.id"),ondelete="CASCADE")
    debt = relationship("Debt", back_populates="payments")
    amount = Column(DECIMAL, nullable=False, index=True) #cantidad a pagar CUOTAS
    due_date = Column(DateTime, index=True) #todos los meses el mismo dia por la cantidad de meses que se indico
    paid = Column(Boolean, nullable=False, default=False)
    paid_at = Column(DateTime, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    company = relationship("Company", back_populates="company_payments")
    status = Column(String, default="pending")#pending, paid, cancelled, overdue (overdue = atrasado)