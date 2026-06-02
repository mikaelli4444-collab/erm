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

def update_contact(session, contact_id, user, name, email, phone, type):
    if not user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User not authenticated")
    
    contact = session.query(Contacts).filter(Contacts.id == contact_id, Contacts.company_id == user.company_id).first()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="404")

    contact.name = name
    contact.email = email
    contact.phone = phone
    contact.type = type

    session.commit()
    session.refresh(contact)

    return {
        "message": "Contact updated successfully",
        "contact": contact,
    }
    
def delete_contact(session, contact_id, user):
    if not user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User not authenticated")
    
    contact = session.query(Contacts).filter(Contacts.id == contact_id, Contacts.company_id == user.company_id).first()
    
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="404")
    
    session.delete(contact)
    session.commit()

    
    return{
        "message": "Contact deleted successfully"
    }
    