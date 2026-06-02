from enum import Enum

class StatusEnum(str, Enum):
    planning = "planning"
    cutting = "cutting"
    pre_assembly = "pre_assembly"
    lamination = "lamination"
    truck_loading = "truck_loading"
    installation = "installation"
    completed = "completed"
    cancelled = "cancelled"

class DebtStatusEnum(str, Enum):
    pending = "pending"
    cancelled = "cancelled"
    paid = "paid"
    overdue = "overdue"
    
class TransactionTypeEnum(str, Enum):
    income = "income"
    expense = "expense"

class TransactionCategoryEnum(str, Enum):
    sale = "sale"
    rent = "rent"
    other_income = "other_income" #idk how to call this lol
    salary = "salary"
    purchases = "purchases"
    utilities = "utilities"
    debt_payment = "debt_payment"
    receivable_payment = "receivable_payment"
    material = "material"
    
class ReceivablesStatusEnum(str, Enum):
    pending = "pending"
    paid = "paid"
    cancelled = "cancelled"
    overdue = "overdue"
    
class UserRoleEnum(str, Enum):
    admin = "admin"
    carpenter = "carpenter"
    auxiliary = "auxiliary"

class plansEnum(str, Enum):
    basic = "basic"
    premium = "premium"
    enterprise = "enterprise"
    
class SubscriptionStatusEnum(str, Enum):
    active = "active"
    canceled = "canceled"
    overdue = "overdue"
    pending = "pending"
    expired = "expired"
    
class SubscriptionCycle(str, Enum):
    MONTHLY = "MONTHLY"
    ANNUALLY = "ANNUALLY"