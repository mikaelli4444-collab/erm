from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from users.users_model import User
from core.security import bcrypt_context
import random
from datetime import datetime, timedelta, timezone
from core.email_service import send_verification_email
from core.config import VERIFICATION_TOKEN_EXPIRE_MINUTES
from users.users_model import Company
from users.users_schema import CompanySchema
from core.config import SECRET_KEY, ALGORITHM
from jose import jwt

def authuser(identifier: str, password: str, session: Session):
    user = session.query(User).filter((User.username == identifier) | (User.email == identifier)).first()

    if not user:
        return None

    if not bcrypt_context.verify(password, user.password):
        return None

    return user

async def generate_and_send_verification_code(user: User, session: Session):
    code = str(random.randint(100000, 999999))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES)
    user.verification_code = code
    user.verification_code_expires_at = expires_at
    session.add(user)
    session.commit()
    session.refresh(user)
    await send_verification_email(user.email, code)
    return user

def verify_user_email(user: User, code: str, session: Session):
    if not user.verification_code or user.verification_code != code:
        return False
    if user.verification_code_expires_at < datetime.now(timezone.utc):
        return False
    user.is_verified = 1
    user.verification_code = None
    user.verification_code_expires_at = None
    session.add(user)
    session.commit()
    session.refresh(user)
    return True

def create_company(request, session, company_name, legal_name, tax_id, email, plan):
    user_id_cookie = request.cookies.get("access_token")
    
    if not user_id_cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(user_id_cookie, SECRET_KEY, algorithms=[ALGORITHM])
        
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    sub = payload.get("sub")

    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = int(sub)
    
    user = session.query(User).filter(User.id == user_id).first() 
    
    if not user: 
        raise HTTPException(status_code=401, detail="User not found")
    
    company_data = CompanySchema(
        name=company_name,
        legal_name=legal_name,
        tax_id=tax_id,
        email=email,
        plan=plan,
        owner_id=user_id,
    )
    
    session.add(company_data)
    session.commit()