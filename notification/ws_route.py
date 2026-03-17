from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_route = APIRouter()

connections = []


@ws_route.websocket("/ws")
async def websocket_notifications(websocket: WebSocket):

    await websocket.accept()
    connections.append(websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        connections.remove(websocket)


# función para enviar mensajes a todos
async def broadcast(message: dict):

    for connection in connections:
        await connection.send_json(message)