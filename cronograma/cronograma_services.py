from fastapi import HTTPException, status
from cronograma.cronograma_models import *
from cronograma.cronograma_schemas import *
import secrets
from core.config import BASE_URL

def create_schedule(session, schedule_data: WeeklyScheduleCreate, company_id: int) -> WeeklySchedule:

    if schedule_data.end < schedule_data.start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date cannot be earlier than start date"
        )
        
    existing = session.query(WeeklySchedule).filter(WeeklySchedule.company_id==company_id,WeeklySchedule.start==schedule_data.start).first()

    if existing:
        raise HTTPException(400, "Schedule already exists for this week.")

    schedule = WeeklySchedule(
        title=schedule_data.title,
        start=schedule_data.start,
        end=schedule_data.end,
        notes=schedule_data.notes,
        company_id=company_id
    )

    session.add(schedule)
    session.commit()
    session.refresh(schedule)

    return schedule

def get_current_schedule(session, company_id: int, start_date: date) -> WeeklySchedule:

    schedule = session.query(WeeklySchedule).filter(WeeklySchedule.company_id == company_id, WeeklySchedule.start == start_date).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active schedule found"
        )

    return schedule

def update_schedule(session, schedule_data: WeeklyScheduleUpdate, company_id: int, start_date: date) -> WeeklySchedule:

    schedule = session.query(WeeklySchedule).filter(WeeklySchedule.company_id == company_id, WeeklySchedule.start == start_date).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    update_data = schedule_data.model_dump(exclude_unset=True)

    new_start = update_data.get("start", schedule.start)
    new_end = update_data.get("end", schedule.end)

    if new_end < new_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date cannot be earlier than start date"
        )

    for field, value in update_data.items():
        setattr(schedule, field, value)

    session.commit()
    session.refresh(schedule)

    return schedule

def delete_schedule(session, schedule_id: int,company_id: int):

    schedule = session.query(WeeklySchedule).filter(WeeklySchedule.id == schedule_id, WeeklySchedule.company_id == company_id).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    session.delete(schedule)
    session.commit()
    
def create_task(session, task_data: ScheduleTaskCreate, company_id: int):

    schedule = session.query(WeeklySchedule).filter(WeeklySchedule.id == task_data.weekly_schedule_id,WeeklySchedule.company_id == company_id).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    task = ScheduleTasks(
        weekly_schedule_id=task_data.weekly_schedule_id,
        day_of_week=task_data.day_of_week.lower(),
        activity=task_data.activity,
        category_id=task_data.category_id,
        order_position=task_data.order_position
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task

def update_task(session, task_id: int, task_data: ScheduleTaskUpdate, company_id: int):

    task = session.query(ScheduleTasks).join(WeeklySchedule,WeeklySchedule.id == ScheduleTasks.weekly_schedule_id).filter(ScheduleTasks.id == task_id,WeeklySchedule.company_id == company_id).first()
    

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    update_data = task_data.model_dump(exclude_unset=True)

    if "day_of_week" in update_data:
        update_data["day_of_week"] = update_data["day_of_week"].lower()

    for field, value in update_data.items():
        setattr(task, field, value)

    session.commit()
    session.refresh(task)

    return task

def delete_task(session,task_id: int,company_id: int):

    task = session.query(ScheduleTasks).join(WeeklySchedule, WeeklySchedule.id == ScheduleTasks.weekly_schedule_id).filter(ScheduleTasks.id == task_id,WeeklySchedule.company_id == company_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    session.delete(task)
    session.commit()
    
def create_milestone(session,milestone_data: WeeklyMilestoneCreate,company_id: int):

    schedule = session.query(WeeklySchedule).filter(WeeklySchedule.id == milestone_data.weekly_schedule_id,WeeklySchedule.company_id == company_id).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    milestone = WeeklyMilestones(
        weekly_schedule_id=milestone_data.weekly_schedule_id,
        description=milestone_data.description,
        completed=False
    )

    session.add(milestone)
    session.commit()
    session.refresh(milestone)

    return milestone

def delete_milestone(session, milestone_id: int, company_id: int):

    milestone = (
        session.query(WeeklyMilestones)
        .join(
            WeeklySchedule,
            WeeklySchedule.id == WeeklyMilestones.weekly_schedule_id
        )
        .filter(
            WeeklyMilestones.id == milestone_id,
            WeeklySchedule.company_id == company_id
        )
        .first()
    )

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    session.delete(milestone)
    session.commit()
    
def toggle_milestone(session, milestone_id: int, company_id: int):

    milestone = session.query(WeeklyMilestones).join(WeeklySchedule,WeeklySchedule.id == WeeklyMilestones.weekly_schedule_id).filter(WeeklyMilestones.id == milestone_id,WeeklySchedule.company_id == company_id).first()

    if not milestone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found"
        )

    milestone.completed = not milestone.completed

    session.commit()
    session.refresh(milestone)

    return milestone

def get_schedule_categories(session, company_id: int):

    categories = session.query(ScheduleCategory).filter(ScheduleCategory.company_id == company_id).order_by(ScheduleCategory.name).all()

    return categories


def create_schedule_category(session, category_data: ScheduleCategoryCreate, company_id: int):

    existing_category = session.query(ScheduleCategory).filter(ScheduleCategory.company_id == company_id,ScheduleCategory.name == category_data.name).first()
    

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )

    category = ScheduleCategory(company_id=company_id, name=category_data.name.strip(), color=category_data.color)

    session.add(category)
    session.commit()
    session.refresh(category)

    return category


def update_schedule_category(session, category_id: int, category_data: ScheduleCategoryUpdate, company_id: int):

    category = session.query(ScheduleCategory).filter(ScheduleCategory.id == category_id,ScheduleCategory.company_id == company_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    update_data = category_data.model_dump(exclude_unset=True)

    if "name" in update_data:
        duplicate = session.query(ScheduleCategory).filter(ScheduleCategory.company_id == company_id,ScheduleCategory.name == update_data["name"],ScheduleCategory.id != category_id).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already exists"
            )

        update_data["name"] = update_data["name"].strip()

    for field, value in update_data.items():
        setattr(category, field, value)

    session.commit()
    session.refresh(category)

    return category


def delete_schedule_category(session, category_id: int, company_id: int):

    category = session.query(ScheduleCategory).filter(ScheduleCategory.id == category_id, ScheduleCategory.company_id == company_id).first()
    

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    tasks_using_category = session.query(ScheduleTasks).filter(ScheduleTasks.category_id == category_id).count()


    if tasks_using_category > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category is being used by one or more tasks"
        )

    session.delete(category)
    session.commit()

def get_schedule_board(session, company_id: int, start_date: date):

    schedule = session.query(WeeklySchedule).filter(WeeklySchedule.company_id == company_id, WeeklySchedule.start == start_date).first()

    if schedule:
        tasks = session.query(ScheduleTasks).filter(ScheduleTasks.weekly_schedule_id == schedule.id).order_by(ScheduleTasks.day_of_week, ScheduleTasks.order_position).all()

        milestones = session.query(WeeklyMilestones).filter(WeeklyMilestones.weekly_schedule_id == schedule.id).all()
        
        categories = session.query(ScheduleCategory).filter(ScheduleCategory.company_id == company_id).all()

        board = {
        "id": schedule.id,
        "title": schedule.title,
        "start": schedule.start,
        "end": schedule.end,
        "notes": schedule.notes,

        "categories": [],

        "days": {
            "segunda": [],
            "terça": [],
            "quarta": [],
            "quinta": [],
            "sexta": [],
            "sabado": [],
            "domingo": []
        },

        "milestones": []
    }

        for task in tasks:
            board["days"][task.day_of_week].append({
                "id": task.id,
                "activity": task.activity,
                "category_id": task.category_id,
                "category_name": task.category.name if task.category else None,
                "category_color": task.category.color if task.category else None,
                "order_position": task.order_position
            })

        for milestone in milestones:
            board["milestones"].append({
                "id": milestone.id,
                "description": milestone.description,
                "completed": milestone.completed
            })

        for category in categories:
            board["categories"].append({
                "id": category.id,
                "name": category.name,
                "color": category.color
            })
    
        return board
    
    else:
        return None
    
def generate_share_link(session, schedule_id: int, company_id: int):

    schedule = session.query(WeeklySchedule).filter(WeeklySchedule.id == schedule_id, WeeklySchedule.company_id == company_id).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    share_token = secrets.token_urlsafe(16)
    link = f"{BASE_URL}/schedule/public/schedule?token={share_token}"

    schedule.shared_token = share_token
    session.commit()
    session.refresh(schedule)

    return {
        "link": link,
        "token": share_token
    }
    
def get_shared_schedule(session, token):

    schedule = session.query(WeeklySchedule).filter(WeeklySchedule.shared_token == token).first()

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared schedule not found"
        )

    tasks = session.query(ScheduleTasks).filter(ScheduleTasks.weekly_schedule_id == schedule.id).order_by(ScheduleTasks.day_of_week, ScheduleTasks.order_position).all()

    milestones = session.query(WeeklyMilestones).filter(WeeklyMilestones.weekly_schedule_id == schedule.id).all()
    
    categories = session.query(ScheduleCategory).filter(ScheduleCategory.company_id == schedule.company_id).all()

    board = {
        "id": schedule.id,
        "title": schedule.title,
        "start": schedule.start,
        "end": schedule.end,
        "notes": schedule.notes,

        "categories": [],

        "days": {
            "segunda": [],
            "terça": [],
            "quarta": [],
            "quinta": [],
            "sexta": [],
            "sabado": [],
            "domingo": []
        },

        "milestones": []
    }

    for task in tasks:
        board["days"][task.day_of_week].append({
            "id": task.id,
            "activity": task.activity,
            "category_id": task.category_id,
            "category_name": task.category.name if task.category else None,
            "category_color": task.category.color if task.category else None,
            "order_position": task.order_position
        })

    for milestone in milestones:
        board["milestones"].append({
            "id": milestone.id,
            "description": milestone.description,
            "completed": milestone.completed
        })

    for category in categories:
        board["categories"].append({
            "id": category.id,
            "name": category.name,
            "color": category.color
        })

    return board

