from pydantic import BaseModel

class SubscriptionRequest(BaseModel):
    plan_id: int
    card_token: str