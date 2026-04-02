from pydantic import BaseModel, Field
from typing import Optional, Literal
from decimal import Decimal
from datetime import date as DATE

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

FinancialTransactionType = Literal[
    "income",
    "expense"
]

FinancialTransactionCategory = Literal[
    "sale",
    "rent",
    "other_income",
    "salary",
    "purchases",
    "utilities",
    "debt_payment",
    "material"
]

class SellsSchema(BaseModel):
    client_name: str = Field(..., min_length=3, max_length=50)
    income: Decimal
    expenses: Decimal
    status: Sellstatus = "planning"
    delivery: DATE
    carpenter_id: Optional[int] = None
    installments: int

    class Config:
        from_attributes = True
        
class DebtCreate(BaseModel):
    amount: Decimal
    creditor: str
    number_of_installments: int = 1
    description: Optional[str] = None
    status: DebtStatus = "pending"
    
class DebtResponse(BaseModel):
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
    due_date: DATE
    paid: bool = False
    status: PaymentStatus = "pending"
    
class PaymentResponse(BaseModel):
    debt_id: int
    amount: Decimal
    due_date: DATE
    paid: bool
    paid_at: Optional[DATE]
    status: PaymentStatus
    company_id: int

    class Config:
        from_attributes = True
        
class ReceivableCreate(BaseModel):
    amount: Decimal
    due_date: DATE
    receiver_id: int
    payer_id: Optional[int] = None
    payer_name: Optional[str] = None
    description: Optional[str] = None
    
class ReceivableResponse(BaseModel):
    amount: Decimal
    due_date: DATE
    receiver_id: int
    payer_id: Optional[int]
    payer_name: Optional[str]
    description: Optional[str]
    company_id: int
    paid_at: Optional[DATE]

    class Config:
        from_attributes = True
        
class FinancialTransactionSchema(BaseModel):
    type: FinancialTransactionType 
    category: FinancialTransactionCategory
    amount: Decimal
    date: DATE = Field(default_factory=DATE.today)
    description: str
    reference_id: int
    is_variable: bool = False