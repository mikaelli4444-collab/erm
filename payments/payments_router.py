from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import RedirectResponse
from core.security import verify_token
from users.users_model import User, Company
from core.dependencies import CreateSession, templates
from payments.payments_services import create_plan, save_plan, create_subscription, update_subscription, get_payment, update_company_status
from sqlalchemy.orm import Session
from payments.payments_models import Plans, Subscription
from payments.payments_schema import SubscriptionRequest

payments_router = APIRouter(prefix="/payment", tags=["payment"])

@payments_router.post("/create_plan")
def create_plan_post(name: str, amount: float, frequency: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):    
    if user.role == "admin":
        
        plan = session.query(Plans).filter(Plans.name == name, Plans.frequency == frequency, Plans.amount == amount).first()
    
        if plan:
            return {
                "id": plan.mp_plan_id,
                "name": plan.name,
                "amount": plan.amount,
                "frequency": plan.frequency,
            }
        
        else:
            planes = save_plan(create_plan(name, amount, frequency), name, amount, frequency, session)
            
            return {
                "id": planes.mp_plan_id,
                "name": planes.name,
                "amount": planes.amount,
                "frequency": planes.frequency,
            }
    
    else:
        raise HTTPException(status_code=403, detail="No autorizado")
    
@payments_router.post("/create_checkout")
def create_checkout_router(plan_id: int = Form(...),user: User = Depends(verify_token),session: Session = Depends(CreateSession)):

    plan = session.query(Plans).filter(Plans.id == plan_id).first()

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Plan no encontrado"
        )

    checkout_url = create_subscription(user,plan,session)

    return RedirectResponse(
        url=checkout_url,
        status_code=303
    )
    
@payments_router.post("/create_subscription")
def create_subscription_router(data: SubscriptionRequest, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    
    plan = session.query(Plans).filter(Plans.id == data.plan_id).first()
    
    return create_subscription(user, plan, data.card_token, session)

@payments_router.post("/update_subscription")
def update_subscription_router(subscription_id: int, status: str, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    subscription = update_subscription(subscription_id, status, session)
    
    if subscription:
        return {
            "id": subscription.id,
            "user_id": subscription.user_id,
            "plan_id": subscription.plan_id,
            "mp_subscription_id": subscription.mp_subscription_id,
            "status": subscription.status
        }
    else:
        raise HTTPException(status_code=404, detail="Suscripción no encontrada")
    
@payments_router.post("/webhook/mercadopago")
async def mp_webhook(request: Request, session: Session = Depends(CreateSession)):

    payload = await request.json()

    print("WEBHOOK:", payload)

    data = payload.get("data")
    if not data:
        return {"error": "no data"}

    payment_id = data.get("id")
    if not payment_id:
        return {"error": "no payment id"}

    payment_data = get_payment(payment_id)

    if not payment_data:
        return {"error": "payment not found"}

    status = payment_data.get("status")

    company_id = payment_data.get("external_reference")

    if not company_id:
        return {"error": "no company reference"}

    if status == "approved":
        update_company_status(company_id, "active", session)

    elif status in ["rejected", "cancelled", "refunded"]:
        update_company_status(company_id, "inactive", session)

    return {"status": "received"}

#VIEWS

@payments_router.get("/plans")
def plans_view(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    plans = session.query(Plans).all()
    return templates.TemplateResponse("payments/plans.html", {"request": request, "plans": plans, "user": user})