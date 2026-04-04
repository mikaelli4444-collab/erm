from fastapi import HTTPException
from datetime import date

ALLOWED_PAYMENT_TRANSITIONS = {
    "pending": ["paid", "overdue", "cancelled"],
    "overdue": ["paid", "cancelled"],
    "paid": [],
    "cancelled": []
}

def change_payment_status(payment, new_status):
    current_status = payment.status

    if new_status not in ALLOWED_PAYMENT_TRANSITIONS[current_status]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition from {current_status} to {new_status}"
        )

    payment.status = new_status
    
    if new_status == "paid":
        payment.paid = True
        payment.paid_at = date.today()

    elif new_status in ["pending", "overdue", "cancelled"]:
        payment.paid = False
        

VALID_RECEIVABLE_TRANSITIONS = {
    "pending": ["paid", "cancelled", "overdue"],
    "overdue": ["paid", "cancelled"],
    "paid": [],
    "cancelled": []
}

def change_receivable_status(receivable, new_status: str):
    current_status = receivable.status

    if current_status not in VALID_RECEIVABLE_TRANSITIONS:
        raise ValueError(f"Invalid current status: {current_status}")

    if new_status not in VALID_RECEIVABLE_TRANSITIONS[current_status]:
        raise ValueError(f"Invalid transition: {current_status} → {new_status}")

    receivable.status = new_status

    if new_status == "paid":
        receivable.paid_at = date.today()