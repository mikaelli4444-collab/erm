import mercadopago
import requests
from core.config import MERCADO_PAGO_ACCESS_TOKEN, BACK_URL
from payments.payments_models import Plans, Subscription
from users.users_model import User

def create_plan(name: str, amount: float, frequency: int):
    url = "https://api.mercadopago.com/preapproval_plan"

    headers = {
        "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "reason": f"Subscription {name} plan for ERM",
        "auto_recurring": {
            "frequency": frequency,
            "frequency_type": "months",
            "transaction_amount": amount,
            "currency_id": "BRL"
        },
        "back_url": BACK_URL
    }

    try:
        response = requests.post(url, json=data, headers=headers)

        if response.status_code != 201:
            print("STATUS:", response.status_code)
            print("RESPONSE:", response.json())
            raise ValueError("Error creando plan en Mercado Pago")

        return response.json()["id"]

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
    
def select_plan(plan_id, session):
    plan = session.query(Plans).filter(Plans.id == plan_id).first()

    return plan

def create_subscription(user, plan, card_token, session):
    
    if not user:
        raise ValueError("Usuario no encontrado en la base de datos")
    
    company = user.company
    
    #quiero que solo el owner pueda crear la subscripcion, entonces los empleados heredan las subscripcion del owner
    
    subscription = session.query(Subscription).filter(Subscription.company_id == company.id, Subscription.status == "active").first()

    if subscription:
        raise ValueError("Ya existe una suscripción activa para esta empresa")
    
    if not plan:
        raise ValueError("Plan no encontrado en la base de datos")
    
    if not isinstance(card_token, str):
        raise ValueError("Token de tarjeta debe ser una cadena de texto")
    
    if card_token is None or card_token.strip() == "":
        raise ValueError("Token de tarjeta no válido")
    
    url = "https://api.mercadopago.com/preapproval"
    
    data = {
        "preapproval_plan_id": plan.mp_plan_id,
        "payer_email": user.email,
        "card_token_id": card_token,
        "back_url": BACK_URL,
        "status": "authorized"
    }
    
    headers = {
        "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=data, headers=headers, timeout=10)
    
    if response.status_code not in [200, 201]:  
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.json())
        raise ValueError("Error creando suscripción en Mercado Pago")
    
    response_data = response.json()
    
    status = response_data.get("status")

    if status not in ["authorized", "pending"]:
        raise ValueError(f"Estado inesperado: {status}")
    
    if "id" not in response_data:
        raise ValueError("MP no devolvió subscription_id")

    return {
    "id": response_data["id"],
    "status": response_data["status"]
}
    
def save_subscription(user, plan, mp_subscription, session):
    subscription = Subscription(
        user_id=user.id,
        plan_id=plan.id,
        mp_subscription_id=mp_subscription["id"],
        status=mp_subscription["status"]
    )
    session.add(subscription)
    #falta hacer el commit que lo hare en el router
    
def update_subscription(mp_subscription_id, status, session):
    subscription = Subscription(
        status=status
    )
    
    session.add(subscription)
    session.commit()
    
def webhook_handler(data):
    mp_subscription_id = data["id"]

    # consultas a Mercado Pago o usas data directa
    status = data["status"]

    update_subscription(mp_subscription_id, status)