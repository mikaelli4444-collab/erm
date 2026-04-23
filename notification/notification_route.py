from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from core.security import verify_token
from users.users_model import User, CompanyJoinRequest
from notification.notification_model import Notification
from notification.notification_services import create_notification, notify_company_join, show_notifications
from users.users_model import Company

notification_router = APIRouter(prefix="/notification",tags=["notification"])


@notification_router.get("/notifications")
async def get_notifications(session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    return await show_notifications(session, user)

@notification_router.post("/notifications/join-request")
async def join_request(request_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    await notify_company_join(request_id, session, user)

@notification_router.post("/notifications/join-company")
async def join_company(company_name: str, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    if user.company_id is not None:
        raise HTTPException(status_code=409, detail="Ya perteneces a una empresa")

    company = session.query(Company).filter(Company.name.ilike(company_name.strip())).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

    existing_request = session.query(CompanyJoinRequest).filter(
        CompanyJoinRequest.user_id == user.id,
        CompanyJoinRequest.company_id == company.id,
        CompanyJoinRequest.status == "pending"
    ).first()
    
    if existing_request:
        raise HTTPException(status_code=409, detail="Ya has enviado una solicitud a esta empresa")

    message = {
        "type": "company_join_request",
        "data": {
            "username": user.username,
            "user_id": user.id,
            "company_id": company.id
        }
    }

    join_request = CompanyJoinRequest(
        user_id=user.id,
        company_id=company.id,
        message=message
    )
    session.add(join_request)
    session.commit()
    session.refresh(join_request)

    await create_notification(company.owner_id, company.id, message, session)

    return {"status": "request_sent"}

@notification_router.post("/notifications/join-request/accept")
async def accepted_request(request_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    request = session.query(CompanyJoinRequest).filter(CompanyJoinRequest.id == request_id).first()
    notification = session.query(Notification).filter(Notification.data['join_request_id'].astext == str(request_id)).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.company.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Authentication error")

    user_to_add = session.query(User).get(request.user_id)

    if user_to_add.company_id != None:
        raise HTTPException(status_code=409, detail="Request error, user actually have a company")
    
    user_to_add.company_id = request.company_id

    session.delete(request)
    if notification:
        session.delete(notification)
        
    session.commit()

    return {"status": "accepted"}

@notification_router.post("/notifications/join-request/reject")
async def rejected_request(request_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    request = session.query(CompanyJoinRequest).filter(CompanyJoinRequest.id == request_id).first()
    notification = session.query(Notification).filter(Notification.data['join_request_id'].astext == str(request_id)).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.company.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Authentication error")

    session.delete(request)
    if notification:
        session.delete(notification)
        
    session.commit()

    return {"status": "rejected"}

@notification_router.patch("/notifications/{notification_id}")
def mark_as_read(notification_id: int,user: User = Depends(verify_token),session: Session = Depends(CreateSession)):

    notification = (session.query(Notification).filter(Notification.id == notification_id).filter(Notification.user_id == user.id).first())

    if notification:
        notification.is_read = True
        session.commit()

    return {"status": "ok"}