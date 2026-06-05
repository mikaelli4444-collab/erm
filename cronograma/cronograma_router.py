from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from users.users_model import User
from core.security import verify_token
from cronograma.cronograma_schemas import *
from cronograma.cronograma_services import *

cronograma_router = APIRouter(prefix="/schedule",tags=["Schedule"])

@cronograma_router.post("/")
def create_new_schedule(schedule_data: WeeklyScheduleCreate,session: Session = Depends(CreateSession),current_user: User = Depends(verify_token)):

    return create_schedule(
        session=session,
        schedule_data=schedule_data,
        company_id=current_user.company_id
    )
    
@cronograma_router.get("/current")
def get_active_schedule(session: Session = Depends(CreateSession),current_user: User = Depends(verify_token)):

    return get_current_schedule(
        session=session,
        company_id=current_user.company_id
    )
    
@cronograma_router.put("/")
def update_active_schedule(schedule_data: WeeklyScheduleUpdate,session: Session = Depends(CreateSession),current_user: User = Depends(verify_token)):

    return update_schedule(
        session=session,
        schedule_data=schedule_data,
        company_id=current_user.company_id
    )
    
@cronograma_router.delete("/{schedule_id}")
def remove_schedule(schedule_id: int,session: Session = Depends(CreateSession),current_user: User = Depends(verify_token)):

    delete_schedule(
        session=session,
        schedule_id=schedule_id,
        company_id=current_user.company_id
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@cronograma_router.post("/tasks")
def create_new_task(task_data: ScheduleTaskCreate,session: Session = Depends(CreateSession),current_user: User = Depends(verify_token)):

    return create_task(
        session=session,
        task_data=task_data,
        company_id=current_user.company_id
    )
    
@cronograma_router.put("/tasks/{task_id}")
def update_existing_task(task_id: int,task_data: ScheduleTaskUpdate,session: Session = Depends(CreateSession),current_user: User = Depends(verify_token)):

    return update_task(
        session=session,
        task_id=task_id,
        task_data=task_data,
        company_id=current_user.company_id
    )
    
@cronograma_router.delete("/tasks/{task_id}")
def remove_task(task_id: int,session: Session = Depends(CreateSession),current_user: User = Depends(verify_token)):

    delete_task(
        session=session,
        task_id=task_id,
        company_id=current_user.company_id
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@cronograma_router.post("/milestones")
def create_new_milestone(milestone_data: WeeklyMilestoneCreate,session: Session = Depends(CreateSession),current_user: User = Depends(verify_token)):

    return create_milestone(
        session=session,
        milestone_data=milestone_data,
        company_id=current_user.company_id
    )
    
@cronograma_router.patch("/milestones/{milestone_id}/toggle",)
def toggle_existing_milestone(milestone_id: int,session: Session = Depends(CreateSession),current_user: User = Depends(verify_token)):

    return toggle_milestone(
        session=session,
        milestone_id=milestone_id,
        company_id=current_user.company_id
    )
    
@cronograma_router.delete("/milestones/{milestone_id}",)
def remove_milestone(milestone_id: int,session: Session = Depends(CreateSession),current_user: User = Depends(verify_token)):

    delete_milestone(
        session=session,
        milestone_id=milestone_id,
        company_id=current_user.company_id
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


#VIEWS


@cronograma_router.get("/board")
def get_board(session: Session = Depends(CreateSession),current_user: User = Depends(verify_token)):

    return get_schedule_board(
        session=session,
        company_id=current_user.company_id
    )