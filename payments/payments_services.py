import mercadopago
from datetime import datetime
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

def create_subscription(user,plan,card_token_id,cpf,payment_method_id,issuer_id,installments,session):

    if not user:
        raise ValueError("Usuario no encontrado")

    print("1")

    company = user.company

    if user.id != company.owner_id:
        raise ValueError("Solo el owner puede pagar")

    if not plan:
        raise ValueError("Plan no encontrado")

    print("2")

    existing_subscription = session.query(
        Subscription
    ).filter(
        Subscription.company_id == company.id,
        Subscription.status == "authorized"
    ).first()

    if existing_subscription:
        raise ValueError(
            "La empresa ya tiene suscripción"
        )

    print("3")

    url = "https://api.mercadopago.com/preapproval"

    data = {
        #"preapproval_plan_id": plan.mp_plan_id, #esta linea me estaba dando problema
        "card_token_id": card_token_id,
        "payment_method_id": payment_method_id,
        "issuer_id": issuer_id,

        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "transaction_amount": float(plan.amount),
            "currency_id": "BRL"
        },

        "payer_email": user.email,
        
        "payer": {
            "identification": {
                "type": "CPF",
                "number": cpf
            }
        },

        "reason":
            f"Subscription for {plan.name}",
            
        "external_reference":
            f"{company.id}:{plan.id}",
            
        "back_url": BACK_URL,
        "status": "authorized",
        "notification_url":
            "https://ooze-crave-yam.ngrok-free.dev/payment/webhook/mercadopago"
    }

    headers = {
        "Authorization":
            f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
        "Content-Type":
            "application/json"
    }

    print("4")

    response = requests.post(
        url,
        json=data,
        headers=headers,
        timeout=15
    )

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    if response.status_code not in [200, 201]:
        raise ValueError(
            f"Error creando suscripción: {response.text}"
        )

    response_data = response.json()

    checkout_url = response_data.get("init_point")

    if not checkout_url:
        raise ValueError(
            "Mercado Pago no devolvió init_point"
        )

    subscription = Subscription(
        user_id=user.id,
        company_id=company.id,
        plan_id=plan.id,
        status="pending",
        amount=plan.amount,
        mp_subscription_id=response_data.get("id")
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

def update_company_value(company_id, plan, session):
    company = session.query(Company).filter(Company.id == company_id).first()
    
    if company:
        company.plan = plan
        session.commit()
        
        return company_id
    
    else:
        raise ValueError("Empresa no encontrada para actualizar suscripción")
    
def get_payment(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"

    headers = {
        "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    return response.json()