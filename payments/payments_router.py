import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from core.dependencies import templates, CreateSession
from users.users_model import User
from core.security import verify_token
from payments.payments_models import Subscription, Plans
from payments.payments_services import select_plan, create_subscription, update_subscription, update_company_value, create_plan
from payments.webhook import verify_webhook
from utilities.limiter.limiter import limiter

payments_router = APIRouter(prefix="/payments", tags=["Payments"])

@payments_router.post("/create-plan")
@limiter.limit("5/minute")
def create_plan_route(request: Request, payload: dict, session: Session = Depends(CreateSession)):
    return create_plan(name=payload["name"], amount=payload["amount"], frequency=payload["frequency"], session=session)


@payments_router.post("/update-plan/{plan_id}")
@limiter.limit("1/minute")
def update_plan_route(request: Request, plan_id: int, payload: dict, session: Session = Depends(CreateSession)):
    plan = session.query(Plans).filter(Plans.id == plan_id).first()

    if not plan:
        raise HTTPException(status_code=404)

    if "name" in payload:
        plan.name = payload["name"]

    if "amount" in payload:
        plan.amount = payload["amount"]

    if "frequency" in payload:
        plan.frequency = payload["frequency"]

    session.commit()

    return {"status": "updated"}

@payments_router.get("/plans-json")
@limiter.limit("1/minute")
def plans_json(request: Request, session: Session = Depends(CreateSession)):
    plans = session.query(Plans).all()

    return [
        {
            "id": plan.id,
            "name": plan.name,
            "amount": plan.amount,
            "frequency": plan.frequency
        }
        for plan in plans
    ]

@payments_router.post("/subscribe/{plan_id}")
@limiter.limit("2/minute")
async def subscribe_logic(request: Request, plan_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    plan = select_plan(plan_id, session)
    if not plan:
        raise HTTPException(status_code=404, detail="404")

    new_sub = Subscription(
        user_id=user.id,
        company_id=user.company_id,
        plan_id=plan.id,
        status="PENDING",
        provider_subscription_id=None,
        payment_provider_id=None,
        amount=plan.amount,
        current_period_start=None,
        current_period_end=None,
        cancel_at_period_end=None,
        is_active=False
        
    )
    session.add(new_sub)
    session.commit()
    
    payment_url = create_subscription(
        email=user.email,
        product_id=plan.external_id,
        external_id=str(new_sub.id)
    )

    if not payment_url or "Error" in str(payment_url):
        raise HTTPException(status_code=400)
        
    return {
        "status": "success", 
        "payment_url": payment_url
        }

@payments_router.post("/webhook/signature")
@limiter.limit("10/minute")
async def abacate_pay_webhook(request: Request, session: Session = Depends(CreateSession)):

    body_bytes = await verify_webhook(request)

    try:
        data = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event = data.get("event")
    payload = data.get("data")

    if event == "subscription.completed":
        try:
            sub_id = int(payload["externalId"])
        except (KeyError, ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid externalId")

        subscription = session.query(Subscription).filter(Subscription.id == sub_id).first()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        if subscription.status == "ACTIVE":
            return {"status": "already_processed"}
        

        subscription.is_active = True
        subscription.payment_provider_id = payload.get("id")
        subscription.provider_subscription_id = payload.get("subscriptionId")

        update_subscription(subscription, "ACTIVE", session)
        update_company_value(subscription.company_id, subscription.plan_id, session)
            
    return {"status": "200"}

#VIEWS

@payments_router.get("/plans")
# @limiter.limit("5/minute")
def plans_view(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)): 
    """Renderiza la página de selección de planes."""
    plans = session.query(Plans).order_by(Plans.id).all()
     
    return templates.TemplateResponse("plans/plans.html", {
        "request": request,
        "plans": plans,
        "user": user,
        "userEmail": user.email,
        "amount": plans[0].amount if plans else 0,
        "plan_basic_id": plans[0].id if len(plans) > 0 else None,
        "plan_premium_id": plans[1].id if len(plans) > 1 else None,
        "plan_enterprise_id": plans[2].id if len(plans) > 2 else None,
        "plan_annual_id": plans[3].id if len(plans) > 3 else None,
        "plan_basic_price": plans[0].amount/100 if len(plans) > 0 else 0,
        "plan_premium_price": plans[1].amount/100 if len(plans) > 1 else 0,
        "plan_enterprise_price": plans[2].amount/100 if len(plans) > 2 else 0,
        "plan_annual_price": plans[3].amount/100 if len(plans) > 3 else 0,
        "descuento": round((plans[2].amount * 12) - plans[3].amount, 2) if len(plans) > 3 else 0
    })
    
@payments_router.get("/success")
@limiter.limit("5/minute")
def success_view(request: Request, user: User = Depends(verify_token)):
    return templates.TemplateResponse("payments/pay_success.html", {
        "request": request,
        "user": user
    })
    
@payments_router.get("/pending")
@limiter.limit("5/minute")
def pending_view(request: Request, user: User = Depends(verify_token)):
    return templates.TemplateResponse("payments/pay_pending.html", {
        "request": request,
        "user": user
    })
    
@payments_router.get("/failure")
@limiter.limit("5/minute")
def failure_view(request: Request, user: User = Depends(verify_token)):
    return templates.TemplateResponse("payments/pay_failure.html", {
        "request": request,
        "user": user
    })

@payments_router.get("/create-plan")
@limiter.limit("5/minute")
def create_plan_page(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    print(user)
    print(session)
    return templates.TemplateResponse("plans/create_plans.html", {
        "request": request,
        "user": user
    })