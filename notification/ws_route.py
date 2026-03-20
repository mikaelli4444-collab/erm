from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from notification.notification_services import manager
from core.database import SessionLocal
from core.security import get_user_from_token


ws_route = APIRouter()


@ws_route.websocket("/ws")
async def websocket_notifications(websocket: WebSocket):

    session = SessionLocal()

    try:

        token = websocket.query_params.get("token")

        if not token:
            await websocket.close()
            return

        user = get_user_from_token(token, session)

        company_id = user.company_id

        await manager.connect(websocket, user.id, company_id)

        try:
            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            manager.disconnect(websocket, user.id, company_id)

    finally:
        session.close()