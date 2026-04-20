from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from users.users_model import User, Company, CompanyJoinRequest
from notification.notification_services import manager, create_notification, notify_company_join
from core.security import bcrypt_context
from core.dependencies import CreateSession
from core.security import create_token, create_verification_token, verify_verification_token, create_refresh_token
from fastapi.security import OAuth2PasswordRequestForm
from users.users_service import authuser, generate_and_send_verification_code, verify_user_email, create_company
from core.dependencies import templates
from core.config import SECRET_KEY, ALGORITHM
from utilities.net.autorouter import use_autorouter
from jose import jwt

home_router = APIRouter(prefix="/home", tags=["home"])

@home_router.post("/login")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(CreateSession)):
    user = authuser(form_data.username, form_data.password, session)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    if not user.is_verified:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "email": user.email, 
            "message": "Please verify your email address before logging in."
        })

    access_token = create_token(user.id)
    refresh_token = create_refresh_token(user.id)

    response = RedirectResponse(url="/inv/dashboard", status_code=303)
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False, #mantener este valor en false en desarrollo y true en produccion porque puede hacer que la cookie no se guarde
        samesite="lax"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False, #mantener este valor en false en desarrollo y true en produccion porque puede hacer que la cookie no se guarde
        samesite="lax"
    )

    return response
    

@home_router.post("/signup")
async def create_user(request: Request, session: Session = Depends(CreateSession), company: str = Form(None), fullname: str = Form(...), username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    
    user = session.query(User).filter((User.email==email) | (User.username==username)).first()
    
    try:
        print("ENTRÓ AL SIGNUP NUEVO")
        if user:
            return templates.TemplateResponse("home/signup.html", {
                "message": "User with this email or username already exists",
                "request": request})
        
        if len(password) < 8:
            return templates.TemplateResponse("home/signup.html", {
                "message": "Password must be at least 8 characters long",
                "request": request})
            
        password = bcrypt_context.hash(password)

        company_obj = session.query(Company).filter(Company.name == company).first()

        new_user = User(
            username=username,
            email=email,
            password=password,
            fullname=fullname,
        )

        session.add(new_user)
        session.flush()
        session.refresh(new_user)
        
        session.commit()

        verification_jwt = create_verification_token(new_user.email)

        if company_obj:
            join_request = CompanyJoinRequest(
            user_id=new_user.id,
            company_id=company_obj.id,
            )
            
            session.add(join_request)
            session.commit()
            session.refresh(join_request)

            await notify_company_join(join_request.id, session, new_user)

            await create_notification(company_obj.owner_id, company_obj.id, join_request.message, session)
            
            owner_id = company_obj.owner_id
            
            try:
                await manager.send_to_user(owner_id, join_request.message)
        
            except:
                pass
            
        else:
            pass

        await generate_and_send_verification_code(new_user, session)

        user_email = new_user.email

        return templates.TemplateResponse("home/verify_email.html", {
            "request": request,
            "verification_jwt": verification_jwt,
            "message": "A verification code has been sent to your email.",
            "user_email": user_email
        })
    
    except Exception as e:
        session.rollback()
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


@home_router.post("/verify-email")
async def verify_email(request: Request,session: Session = Depends(CreateSession), code: str = Form(...), verification_jwt: str = Form(...)):

    email = verify_verification_token(verification_jwt)

    if not email:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "message": "Token inválido o expirado.",
            "verification_jwt": verification_jwt 
        })

    user = session.query(User).filter(User.email == email).first()
    if not user:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "message": "Usuario no encontrado.",
            "verification_jwt": verification_jwt
        })
    
    if verify_user_email(user, code, session):
        return RedirectResponse(url="/home/login", status_code=status.HTTP_303_SEE_OTHER)
    else:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "email": email, 
            "verification_jwt": verification_jwt,
            "message": "Código inválido o expirado."
        })


@home_router.post("/resend-verification-email")
async def resend_verification_email(request: Request, session: Session = Depends(CreateSession), verification_jwt: str = Form(...)):
    email = verify_verification_token(verification_jwt)
    if not email:
        return templates.TemplateResponse("home/login_email.html", {
            "request": request, 
            "message": "Invalid or expired verification link. Please try logging in again."
        })

    user = session.query(User).filter(User.email == email).first()
    if not user:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "message": "User not found. Please register or log in."
        })
    
    if user.is_verified:

        return RedirectResponse(url="/home/login", status_code=status.HTTP_303_SEE_OTHER)

    await generate_and_send_verification_code(user, session)
    
    new_verification_jwt = create_verification_token(user.email)

    return templates.TemplateResponse("home/verify_email.html", {
        "request": request, 
        "email": user.email,
        "verification_jwt": new_verification_jwt,
        "message": "A new verification code has been sent to your email."
    })

@home_router.post("/create-company")
def create_company_router(request: Request, session: Session = Depends(CreateSession), company_name: str = Form(...), legal_name: str = Form(...), tax_id: str = Form(...), email: str = Form(...)):
    company = create_company(request, session, company_name, legal_name, tax_id, email)
    
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = int(payload.get("sub"))

    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.company_id = company.id

    session.commit()

    return RedirectResponse(url="/home/plans", status_code=303)

#VIEWS

use_autorouter(
    home_router, 
    templates, 
    '/home'
)

@home_router.post("/refresh")
def refresh_token(request: Request, session: Session = Depends(CreateSession)):
    
    refresh_token_cookie = request.cookies.get("refresh_token")
    
    if not refresh_token_cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(refresh_token_cookie, SECRET_KEY, algorithms=[ALGORITHM])
        
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    sub = payload.get("sub")

    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = int(sub)
    
    user = session.query(User).filter(User.id == user_id).first() 
    
    if not user: 
        raise HTTPException(status_code=401, detail="User not found")
    
    new_access = create_token(user_id)
    
    response = JSONResponse(content={"message": "refreshed"})
    
    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=False, #mantener este valor en false en desarrollo y true en produccion porque puede hacer que la cookie no se guarde
        samesite="lax"
    )
     
    return response