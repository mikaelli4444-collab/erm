from pydantic import BaseModel, Field
from datetime import date
from core.enum.enum import WeekDayEnum

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
    day_of_week: WeekDayEnum
    activity: str
    category_id: int | None = None
    order_position: int
    
class ScheduleTaskUpdate(BaseModel):
    day_of_week: WeekDayEnum | None = None
    activity: str | None = None
    category_id: int | None = None
    order_position: int | None = None
    
class WeeklyMilestoneCreate(BaseModel):
    weekly_schedule_id: int
    description: str
    
class WeeklyMilestoneToggle(BaseModel):
    completed: bool
    
class ScheduleCategoryCreate(BaseModel):
    name: str
    color: str

class ScheduleCategoryUpdate(BaseModel):
    name: str | None = None
    color: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )