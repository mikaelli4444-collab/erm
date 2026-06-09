import requests
from core.config import ABACATE_PAY_KEY
from payments.payments_models import Plans
from users.users_model import Company
from dataclasses import dataclass
from core.enum.enum import SubscriptionCycle
from typing import Optional

@dataclass
class Plan:
    """Estructura de un plan de suscripción."""
    external_id: str
    name: str
    price_cents: int  # Valor en centavos para evitar problema de punto flotante
    cycle: SubscriptionCycle
    description: Optional[str] = None
    image_url: Optional[str] = None


def create_plan(name: str, amount: float, frequency: int, session):
    url = "https://api.abacatepay.com/v2/products/create"

    headers = {
        "Authorization": f"Bearer {ABACATE_PAY_KEY}",
        "Content-Type": "application/json"
    }

    price_in_cents = int(amount * 100)


    cycle_map = {
        1: "MONTHLY",
        12: "ANNUALLY"
    }

    cycle = cycle_map.get(frequency, "MONTHLY")

    data = {
        "externalId": f"plan_{name.lower()}",
        "name": name,
        "price": int(amount * 100),
        "currency": "BRL",
        "cycle": cycle
    }

    response = requests.post(url, json=data, headers=headers, timeout=15)

    if response.status_code not in [200, 201]:
        raise ValueError(f"Error creando plan en AbacatePay: {response.text}")
    
    data = response.json()
    
    plan = Plans(
        name=name,
        amount=amount,
        frequency=frequency,
        external_id=data["id"]
    )
    session.add(plan)
    session.commit()

    return {
        "plan_id": plan.id,
        "external_id": plan.external_id
        }
    
def get_subscription_status(subscription_id):
    # En AbacatePay, las suscripciones se consultan a través del ID del checkout generado
    url = f"https://api.abacatepay.com/v2/checkouts/one?id={subscription_id}"

    headers = {
        "Authorization": f"Bearer {ABACATE_PAY_KEY}"
    }

    response = requests.get(url, headers=headers )

    if response.status_code != 200:
        return None

    return response.json()["data"]


def select_plan(plan_id, session):
    plan = session.query(Plans).filter(Plans.id == plan_id).first()
    return plan

def create_subscription(email, product_id, external_id=None):
    url = "https://api.abacatepay.com/v2/subscriptions/create"
    
    headers = {
        "Authorization": f"Bearer {ABACATE_PAY_KEY}",
        "Content-Type": "application/json"
    }
    
    customer_url = "https://api.abacatepay.com/v2/customers/create"
    customer_res = requests.post(customer_url, headers=headers, json={"email": email} )
    
    if customer_res.status_code not in [200, 201]:
        return f"Error creando cliente en AbacatePay: {customer_res.text}"
    
    customer_id = customer_res.json()["data"]["id"]

    payload = {
        "customerId": customer_id,
        "items": [
            {
                "id": product_id,
                "quantity": 1
            }
        ],
        "externalId": external_id
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code not in [200, 201]:
        return f"Error creando suscripción en AbacatePay: {response.text}"

    # Devolvemos la URL donde el usuario debe pagar
    return response.json()["data"]["url"]

    
def update_subscription(subscription, status, session):
    subscription.status = status
    session.commit()
    return subscription


def update_company_value(company_id, plan, session):
    company = session.query(Company).filter(Company.id == company_id).first()
    
    if company:
        company.plan = plan
        session.commit()
        
        return company_id
    
    else:
        raise ValueError("404")
    
def get_payment_status(checkout_id):
    url = f"https://api.abacatepay.com/v2/checkouts/one?id={checkout_id}"

    headers = {
    "Authorization": f"Bearer {ABACATE_PAY_KEY}"
    }

    response = requests.get(url, headers=headers )

    if response.status_code != 200:
        return f"Error obteniendo estado de pago: {response.text}"

    return response.json()["data"]