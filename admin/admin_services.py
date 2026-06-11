import requests
from core.config import ABACATE_PAY_KEY, ABACATE_BASE_URL
from payments.payments_models import Plans
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


def create_plan(user, name: str, amount: float, frequency: int, session):
    if user.role != "admin":
        raise ValueError("Unauthorized")

    url = f"{ABACATE_BASE_URL}/products/create"

    price_in_cents = int(amount * 100)

    cycle_map = {
        1: "MONTHLY",
        12: "ANNUALLY"
    }

    cycle = cycle_map.get(frequency, "MONTHLY")

    payload = {
        "externalId": f"plan_{name.lower()}_{uuid4().hex[:8]}",
        "name": name,
        "price": price_in_cents,
        "currency": "BRL",
        "cycle": cycle
    }

    response = requests.post(url, json=payload, headers=HEADERS, timeout=15)
    
    print("STATUS:", response.status_code)
    print("TEXT:", response.text)
    
    data = _safe_response(response)

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