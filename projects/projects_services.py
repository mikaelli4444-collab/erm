from fastapi import HTTPException
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import date
from users.users_model import User
from projects.projects_schema import CreateProject
from projects.projects_model import Projects 


def create_project(user: User, session: Session, data: CreateProject):
    new_project = Projects(
        name=data.name,
        carpenter=data.carpenter,
        client_name=data.client_name,
        delivery=data.delivery,
        description=data.description,
        address=data.address,
        company_id=user.company_id
    )
    session.add(new_project)
    session.commit()
    session.refresh(new_project)
    return new_project

def save_image