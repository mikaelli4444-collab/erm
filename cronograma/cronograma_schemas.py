from pydantic import BaseModel
from datetime import date
from core.enum.enum import TaskStatusEnum

class WeeklyScheduleCreate(BaseModel):
    title: str
    start: date
    end: date
    notes: str | None = None
    
class WeeklyScheduleUpdate(BaseModel):
    title: str | None = None
    start: date | None = None
    end: date | None = None
    notes: str | None = None
    
class ScheduleTaskCreate(BaseModel):
    weekly_schedule_id: int
    day_of_week: str
    activity: str
    stage: TaskStatusEnum
    order_position: int
    
class ScheduleTaskUpdate(BaseModel):
    day_of_week: str | None = None
    activity: str | None = None
    stage: TaskStatusEnum | None = None
    order_position: int | None = None
    
class WeeklyMilestoneCreate(BaseModel):
    weekly_schedule_id: int
    description: str
    
class WeeklyMilestoneToggle(BaseModel):
    completed: bool