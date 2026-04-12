from pydantic import BaseModel, Field
from typing import Optional, Literal
from decimal import Decimal
from datetime import date as DATE

class CreateProject(BaseModel):
    name: str
    carpenter: str
    client_name: str
    delivery: DATE
    description: str
    address: str
    