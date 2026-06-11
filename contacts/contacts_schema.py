from pydantic import BaseModel, Field
from typing import Optional
from core.enum.enum import ContactsTypes


class ContactsBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: str
    type: ContactsTypes
    
class ContactUpdate(BaseModel):
    name: str
    email: str | None = None
    phone: str
    type: str