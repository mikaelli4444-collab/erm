from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from users.users_model import User
from core.security import bcrypt_context, verify_token
from core.dependencies import CreateSession
from core.security import create_token, create_verification_token, verify_verification_token
from fastapi.security import OAuth2PasswordRequestForm
from users.users_service import authuser, generate_and_send_verification_code, verify_user_email
from core.dependencies import templates

from utilities.net.autorouter import use_autorouter

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
        verification_jwt = create_verification_token(user.email)
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request,
            "email": user.email,
            "verification_jwt": verification_jwt,
            "message": "Please verify your email address before logging in."
        })

    access_token = create_token(user.id)

    response = RedirectResponse(url="/inv/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax"
    )

    return response

@home_router.get("/refresh")
def refresh_token(user: User = Depends(verify_token)):
    access_token = create_token(user.id)
    return {
        "access_token": access_token, 
        "token_type": "bearer"
     }
    
@home_router.post("/signup")
async def create_user(request: Request, session: Session = Depends(CreateSession), fullname: str = Form(...), username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    user = session.query(User).filter((User.email==email) | (User.username==username)).first()
    
    try:
        if user:
            return templates.TemplateResponse("home/signup.html", {
                "message": "User with this email or username already exists",
                "request": request})
        
        if len(password) < 8:
            return templates.TemplateResponse("home/signup.html", {
                "message": "Password must be at least 8 characters long",
                "request": request})
            
        password = bcrypt_context.hash(password)

        new_user = User(
            username=username,
            email=email,
            password=password,
            fullname=fullname
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        user_email = new_user.email
        verification_jwt = create_verification_token(new_user.email)

        try:
            await generate_and_send_verification_code(new_user, session)
            message = "A verification code has been sent to your email."
        except Exception as e:
            message = "Usuario creado. No se pudo enviar el correo; usá 'Reenviar código' para recibir el código por email."

        return templates.TemplateResponse("home/verify_email.html", {
            "request": request,
            "verification_jwt": verification_jwt,
            "message": message,
            "user_email": user_email,
            "email": user_email
        })

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=401, detail=f"Error creating user: {str(e)}")

use_autorouter(
    home_router, 
    templates, 
    '/home'
)


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
    else:\
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

    try:
        await generate_and_send_verification_code(user, session)
        new_verification_jwt = create_verification_token(user.email)
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request,
            "email": user.email,
            "verification_jwt": new_verification_jwt,
            "message": "A new verification code has been sent to your email."
        })
    except Exception:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request,
            "email": user.email,
            "verification_jwt": verification_jwt,
            "message": "No se pudo enviar el correo. Revisá en config.yaml el servidor SMTP (host, usuario, contraseña)."
        })