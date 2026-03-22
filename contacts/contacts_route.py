from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates
from core.security import verify_token
from contacts.contacts_models import Contacts
from contacts.contacts_services import CreateContact
from contacts.contacts_schema import ContactsBase
from users.users_model import User

contacts_router = APIRouter(prefix="/ctc", tags=["ctc"])

@contacts_router.post("/add")
def create_contact(name: str = Form(...), email: str | None = Form(None), phone: str = Form(...), type: str = Form(...), user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    
    contact = ContactsBase(
        name=name,
        email=email,
        phone=phone,
        type=type
    )  

    CreateContact(contact, user, session)
    
    return RedirectResponse(url="/ctc", status_code=303)




#VIEWS

@contacts_router.get("/")
def get_contacts(request: Request, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    
    contacts =  session.query(Contacts).filter(Contacts.company_id == user.company_id).all()


    return templates.TemplateResponse(
        "contacts/contacts.html",
        {
            "request": request,
            "contacts": contacts,
        }
    )