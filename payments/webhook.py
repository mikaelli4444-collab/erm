import hmac
import hashlib
from fastapi import Request, HTTPException, status
from core.config import ABACATE_PAY_WEBHOOK_SECRET

async def verify_webhook(request: Request):

    #obtener el cuerpo crudo de la petición
    raw_body = await request.body()

    #filtrar la firma
    signature = request.headers.get("x-abacatepay-signature")

    if not signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Missing webhook signature"
        )

    #calcular la firma esperada usando el Webhook Secret (no la API Key)
    expected_signature = hmac.new(
        ABACATE_PAY_WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    #comparación segura para evitar ataques de tiempo
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid webhook signature"
        )

    return raw_body