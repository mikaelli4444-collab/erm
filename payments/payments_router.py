from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException 
from fastapi.responses import RedirectResponse 
from core.security import verify_token 
from core.config import PUBLIC_KEY
from users.users_model import User
from core.dependencies import CreateSession, templates 
from payments.payments_services import create_plan, save_plan, create_subscription, update_subscription, get_subscription, update_company_value
from sqlalchemy.orm import Session 
from payments.payments_models import Plans, Subscription 
from payments.prueba import prueba_pago

payments_router = APIRouter(prefix="/payment", tags=["payment"]) 

@payments_router.post("/prueba")
def prueba_view():
    return prueba_pago()

@payments_router.post("/create_plan") 
def create_plan_post(name: str, amount: float, frequency: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
     
    if user.role == "admin": 
        plan = session.query(Plans).filter(Plans.name == name, Plans.frequency == frequency, Plans.amount == amount).first() 
    
        if plan: 
            return { 
                    "id": plan.mp_plan_id, 
                    "name": plan.name, 
                    "amount": plan.amount, 
                    "frequency": plan.frequency 
                    } 
        
        else: 
            planes = save_plan(create_plan(name, amount, frequency), name, amount, frequency, session) 
            
            return { 
                    "id": planes.mp_plan_id, 
                    "name": planes.name, 
                    "amount": planes.amount, 
                    "frequency": planes.frequency
                    } 
    else: 
        raise HTTPException(status_code=403, detail="No autorizado") 

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


@payments_router.post("/create_checkout")
def create_checkout_router(plan_id: int = Form(...),cpf: str = Form(...),card_token_id: str = Form(...),payment_method_id: str = Form(...), issuer_id: str = Form(...),installments: int = Form(...),user: User = Depends(verify_token),session: Session = Depends(CreateSession)):

    try:

        plan = session.query(Plans).filter(
            Plans.id == plan_id
        ).first()

        if not plan:
            raise HTTPException(
                status_code=404,
                detail="Plan no encontrado"
            )

        print("PLAN:", plan.name)
        print("CPF:", cpf)
        print("TOKEN:", card_token_id)
        print("PAYMENT METHOD:", payment_method_id)
        print("ISSUER:", issuer_id)
        print("INSTALLMENTS:", installments)

        checkout_url = create_subscription(
            user=user,
            plan=plan,
            card_token_id=card_token_id,
            cpf=cpf,
            payment_method_id=payment_method_id,
            issuer_id=issuer_id,
            installments=installments,
            session=session
        )

        return RedirectResponse(
            url=checkout_url,
            status_code=303
        )

    except HTTPException as e:

        print("HTTP ERROR:", e.detail)

        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail
        )

    except Exception as e:

        print("GENERAL ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
@payments_router.post("/webhook/mercadopago") 
async def mp_webhook(request: Request, session: Session = Depends(CreateSession)): 
    try:
        payload = await request.json() 
    
        data = payload.get("data")
        
        type_event = payload.get("type")
        
        print(type_event)

        if type_event != "subscription_preapproval":
            return {"message": "ignored"}
        
        if not data: 
            return {"error": "no data"} 
        
        print(payload) 
        
        subscription_id = data.get("id") 
        
        if not subscription_id: 
            return {"error": "no subscription id"} 
        
        subscription_data = get_subscription(subscription_id) 
        
        update_subscription(subscription_id, subscription_data["status"], session) 
        
        subscription = session.query(Subscription).filter(Subscription.mp_subscription_id == subscription_id).first() 
        
        if not subscription:
            return {"error": "subscription not found"}

        company_id = subscription.company_id 
        
        if subscription_data["status"] == "authorized": 
            update_company_value(company_id, subscription.plan.name.value, session) 
            
        elif subscription_data["status"] in ["cancelled", "rejected"]: 
            update_company_value(company_id, "inactive", session) 
            
        return {"status": "received"}

    except Exception as e:
        print("Error processing webhook:", e)

#VIEWS 
@payments_router.get("/plans") 
def plans_view(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)): 
    plans = session.query(Plans).order_by(Plans.id).all()
     
    return templates.TemplateResponse("payments/plans.html", {
        "request": request,
        "plans": plans,
        "user": user,
        "userEmail": user.email,
        "public_key": PUBLIC_KEY,
        "amount": plans[0].amount if plans else 0,
        "plan_basic_id": plans[0].id if len(plans) > 0 else None,
        "plan_premium_id": plans[1].id if len(plans) > 1 else None,
        "plan_enterprise_id": plans[2].id if len(plans) > 2 else None,
        "plan_annual_id": plans[3].id if len(plans) > 3 else None,
        "plan_basic_price": plans[0].amount if len(plans) > 0 else 0,
        "plan_premium_price": plans[1].amount if len(plans) > 1 else 0,
        "plan_enterprise_price": plans[2].amount if len(plans) > 2 else 0,
        "plan_annual_price": plans[3].amount if len(plans) > 3 else 0,
        "descuento": round((plans[2].amount * 12) - plans[3].amount, 2) if len(plans) > 3 else 0
        })
    
@payments_router.get("/success")
def success_view(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    return templates.TemplateResponse("payments/pay_success.html", {
        "request": request,
        "user": user
    })
    
@payments_router.get("/pending")
def pending_view(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    return templates.TemplateResponse("payments/pay_pending.html", {
        "request": request,
        "user": user
    })
    
@payments_router.get("/failure")
def failure_view(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    return templates.TemplateResponse("payments/pay_failure.html", {
        "request": request,
        "user": user
    })