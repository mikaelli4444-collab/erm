import hmac
import hashlib
from fastapi import Request, HTTPException
from core.config import ABACATE_PAY_WEBHOOK_SECRET

async def verify_webhook(request):

    raw_body = await request.body()

    header_secret = request.headers.get("x-webhook-secret")

    if header_secret != ABACATE_PAY_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook secret"
        )

    return raw_body