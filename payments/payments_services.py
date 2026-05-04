import mercadopago
from core.config import MERCADO_PAGO_ACCESS_TOKEN
from payments.payments_models import Plans

def create_plan(name: str, amount: float, frequency: int):
    sdk = mercadopago.SDK(MERCADO_PAGO_ACCESS_TOKEN)

    plan_data = {
        "reason": f"Subscription {name} plan for ERM",
        "auto_recurring": {
            "frequency": frequency,
            "frequency_type": "months",
            "transaction_amount": amount,
            "currency_id": "BRL"
        }
    }

    try:
        result = sdk.preapproval_plan().create(plan_data)
        preapproval = result["response"] 
        return preapproval["id"]

    except Exception as e:
        print("Error creating plan:", e)
        raise ValueError("Failed to create plan in Mercado Pago")

def save_plan(mp_plan_id, name, amount, frequency, session):
    
    plan = session.query(Plans).filter(Plans.name == name, Plans.frequency == frequency, Plans.amount == amount).first()
    
    if plan:
        return {
                "id": plan.mp_plan_id,
                "name": plan.name,
                "amount": plan.amount,
                "frequency": plan.frequency,
            }
            
    plans = Plans(
        mp_plan_id = mp_plan_id,
        name = name,
        amount = amount,
        frequency = frequency
    )
    
    try:
        session.add(plans)
        session.commit()
        return plans
    
    except Exception as e:
        session.rollback()
        raise ValueError(f"Error al subir plan a la DB: {e}")