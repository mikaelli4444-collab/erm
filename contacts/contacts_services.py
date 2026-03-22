from fastapi import HTTPException, status
from contacts.contacts_models import Contacts
from sqlalchemy import or_
from sqlalchemy.orm import Session
from contacts.contacts_schema import ContactsBase
from users.users_model import User

def CreateContact(ctccreate: ContactsBase, user: User, session: Session):
    
    new_contact = Contacts(
        name = ctccreate.name,
        email = ctccreate.email,
        phone = ctccreate.phone,
        type = ctccreate.type,
        company_id = user.company_id
    )

    contact = session.query(Contacts).filter(Contacts.company_id == user.company_id, or_(Contacts.email == ctccreate.email,
                                                                                         Contacts.name == ctccreate.name,
                                                                                         Contacts.phone == ctccreate.phone)
                                                                                         ).first()

    if contact:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User alredy exist")
    
    session.add(new_contact)
    session.commit()
    session.refresh(new_contact)
    
    return new_contact