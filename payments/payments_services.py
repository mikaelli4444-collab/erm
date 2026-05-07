import mercadopago
import requests
from core.config import MERCADO_PAGO_ACCESS_TOKEN, BACK_URL
from payments.payments_models import Plans, Subscription
from users.users_model import User, Company

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

def create_subscription(user, plan, session):

    if not user:
        raise ValueError("Usuario no encontrado en la base de datos")

    company = user.company

    if user.id != company.owner_id: #solo el owner debe pagar y heredar la subscripcion a los empleados
        raise ValueError(
            "No eres digno de pagar esto, ahora vuelve a tu lugar, esclavo"
        )

    if not plan:
        raise ValueError("Plan no encontrado en la base de datos")

    subscription = session.query(Subscription).filter(Subscription.company_id == company.id,Subscription.status == "authorized").first()

    if subscription:
        raise ValueError(
            "Ya existe una suscripción activa para esta empresa"
        )

    url = "https://api.mercadopago.com/checkout/preferences"

    data = {
        "items": [
            {
                "title": str(plan.name),
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(plan.amount)
            }
        ],
        "payer": {
            "email": user.email
        },

        "back_urls": {
            "success": "https://tuapp.com/payment/success",
            "failure": "https://tuapp.com/payment/failure",
            "pending": "https://tuapp.com/payment/pending"
        },

        "notification_url":
        "https://ooze-crave-yam.ngrok-free.dev/payment/webhook/mercadopago"

    }

    headers = {
        "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        json=data,
        headers=headers,
        timeout=10
    )

    if response.status_code not in [200, 201]:
        print("STATUS:", response.status_code)
        print("HEADERS:", headers)
        print("RESPONSE:", response.text)

        raise ValueError(
            "Error creando checkout en Mercado Pago"
        )

    response_data = response.json()
    
    checkout_url = response_data.get("init_point")

    if not checkout_url:
        raise ValueError(
            "MercadoPago no devolvió init_point"
        )

    subscription = Subscription(
        user_id=user.id,
        company_id=company.id,
        plan_id=plan.id,
        status="pending",
        amount=plan.amount
    )

    session.add(subscription)
    session.commit()

    return checkout_url
    
def save_subscription(user, plan, mp_subscription, session):
    subscription = Subscription(
        user_id=user.id,
        plan_id=plan.id,
        mp_subscription_id=mp_subscription["id"],
        status=mp_subscription["status"],
        company_id=user.company_id
    )
    session.add(subscription)
    session.commit()
    
def update_subscription(mp_subscription_id, status, session):
    
    subscription = session.query(Subscription).filter(Subscription.mp_subscription_id == mp_subscription_id).first()
    
    if subscription:
        subscription.status = status
        session.commit()
        return subscription
    
    else:
        raise ValueError("Suscripción no encontrada para actualizar")
    
def get_subscription(mp_subscription_id): #esta funcion es para el futuro, quiero hacer yo mismo el formulario para obtener tarjetas y poder cobrar directamente en mi app
    url = f"https://api.mercadopago.com/preapproval/{mp_subscription_id}"

    headers = {
        "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"
    }
    
    response = requests.get(url, headers=headers)
    
    return response.json()

def update_company_status(company_id, new_status, session):
    company = session.query(Company).filter(Company.id == company_id).first()
    
    if company:
        company.plan = new_status
        session.commit()
        
        return company_id
    
    else:
        raise ValueError("Empresa no encontrada para actualizar estado de suscripción")
    
def get_payment(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"

    headers = {
        "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    return response.json()