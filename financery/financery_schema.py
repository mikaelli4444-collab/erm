from pydantic import BaseModel, Field
from typing import Optional, Literal
from decimal import Decimal
from datetime import date

Sellstatus = Literal[
    "planning",
    "cutting",
    "pre_assembly",
    "lamination",
    "truck_loading",
    "installation",
    "completed",
    "cancelled"
    ]

PaymentStatus = Literal[
    "pending",
    "paid",
    "cancelled",
    "overdue"
]

DebtStatus = Literal[
    "pending",
    "paid",
    "cancelled",
    "overdue"
]

class SellsSchema(BaseModel):
    client_name: str = Field(..., min_length=3, max_length=50)
    income: int
    expenses: int
    status: Sellstatus = "planning"
    delivery: date
    carpenter_id: Optional[int] = None

    class Config:
        from_attributes = True
        
class DebtCreate(BaseModel):
    amount: Decimal
    creditor: str
    number_of_installments: int = 1
    description: Optional[str] = None
    status: DebtStatus = "pending"
    
class DebtResponse(BaseModel):
    id: int
    amount: Decimal
    creditor: str
    number_of_installments: int
    description: Optional[str]
    status: DebtStatus
    company_id: int

    class Config:
        from_attributes = True
    
class PaymentCreate(BaseModel):
    debt_id: int
    amount: Decimal
    due_date: date
    paid: bool = False
    status: PaymentStatus = "pending"
    
class PaymentResponse(BaseModel):
    id: int
    debt_id: int
    amount: Decimal
    due_date: date
    paid: bool
    paid_at: Optional[date]
    status: PaymentStatus
    company_id: int

    class Config:
        from_attributes = True
        
class ReceivableCreate(BaseModel):
    amount: Decimal
    due_date: date
    receiver_id: int
    payer_id: Optional[int] = None
    payer_name: Optional[str] = None
    description: Optional[str] = None
    
class ReceivableResponse(BaseModel):
    id: int
    amount: Decimal
    due_date: date
    receiver_id: int
    payer_id: Optional[int]
    payer_name: Optional[str]
    description: Optional[str]
    company_id: int
    paid_at: Optional[date]

    class Config:
        from_attributes = True