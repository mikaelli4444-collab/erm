import requests
from core.config import ABACATE_PAY_KEY, ABACATE_BASE_URL
from payments.payments_models import Plans
from users.users_model import Company
from uuid import uuid4

HEADERS = {
    "Authorization": f"Bearer {ABACATE_PAY_KEY}",
    "Content-Type": "application/json"
}


def _safe_response(response):
    try:
        data = response.json()
    except Exception:
        raise ValueError("Respuesta inválida de AbacatePay")

    if not data.get("success", False):
        raise ValueError(f"AbacatePay error: {data.get('error')}")

    return data["data"]


def select_plan(plan_id, session):
    return session.query(Plans).filter(Plans.id == plan_id).first()

def create_subscription(email, product_id, external_id=None):
    url = f"{ABACATE_BASE_URL}/subscriptions/create"

    # create customer (AbacatePay deduplica por email/taxId internamente)
    customer_url = f"{ABACATE_BASE_URL}/customers/create"

    customer_res = requests.post(
        customer_url,
        headers=HEADERS,
        json={"email": email},
        timeout=15
    )

    customer_data = _safe_response(customer_res)
    customer_id = customer_data["id"]

    payload = {
        "customerId": customer_id,
        "items": [
            {
                "id": product_id,
                "quantity": 1
            }
        ],
        "externalId": external_id or str(uuid4())
    }

    response = requests.post(url, json=payload, headers=HEADERS, timeout=15)
    data = _safe_response(response)

    # URL de pago (checkout hosted)
    return data["url"]


def get_subscription_status(subscription_id):
    url = f"{ABACATE_BASE_URL}/checkouts/one?id={subscription_id}"

    response = requests.get(url, headers={"Authorization": f"Bearer {ABACATE_PAY_KEY}"}, timeout=15)

    if response.status_code != 200:
        return None

    return _safe_response(response)

def update_subscription(subscription, status, session):
    subscription.status = status
    session.commit()
    return subscription


def update_company_value(company_id, plan, session):
    company = session.query(Company).filter(Company.id == company_id).first()

    if not company:
        raise ValueError("Company not found")

    company.plan = plan
    session.commit()

    return company_id

def get_payment_status(checkout_id):
    url = f"{ABACATE_BASE_URL}/checkouts/one?id={checkout_id}"

    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {ABACATE_PAY_KEY}"},
        timeout=15
    )

    if response.status_code != 200:
        return None

    return _safe_response(response)