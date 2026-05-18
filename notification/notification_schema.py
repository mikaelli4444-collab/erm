from pydantic import BaseModel

class Notification(BaseModel):
    id: int
    user_id: int
    company_id: int
    message: str
    data: dict

    class Config:
        from_attributes = True
        
class JoinRequestNotificationData(BaseModel):
    company_name: str
    
    class Config:
        from_attributes = True