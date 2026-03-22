from fastapi import WebSocket, HTTPException
from sqlalchemy.orm import Session
from notification.notification_model import Notification
from users.users_model import User, Company, CompanyJoinRequest



class ConnectionManager:

    def __init__(self):
        self.company_connections = {} #esto creo el diccionario company_connection en memoria para poder guardar las empresas activas para despues filtrar   #estructura real de memoria
        self.user_connections = {}                                                                                                                           #{
                                                                                                                                                             #  2: [ws1, ws3, ws6...]
                                                                                                                                                             #  9: [ws5, ws7, ws999...]
                                                                                                                                                             #  1: [ws20, ws100, ws8...]
                                                                                                                                                             #}
    async def connect(self, websocket: WebSocket, user_id:int, company_id: int):
        # guardar usuario
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []

        self.user_connections[user_id].append(websocket)

        if company_id not in self.company_connections: #esto es para crear una lista para cada empresa, osea, si la empresa con el id 3 no esta en el diccionario, crea una lista dentro
            self.company_connections[company_id] = []  #del diccionario y comienza a agregar los usuarios activos de cada empresa

        self.company_connections[company_id].append(websocket) #despues de aceptar la conexion esta linea la guarda en el diccionario para saber que esta activa, esto guardara en 
                                                                #la lista ws1, ws2, ws3....


    def disconnect(self, websocket: WebSocket, user_id: int, company_id: int):

        if company_id in self.company_connections:
            if websocket in self.company_connections[company_id]:
                self.company_connections[company_id].remove(websocket)
                
            if not self.company_connections[company_id]:
                del self.company_connections[company_id]

        if user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)

                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]

    async def send_to_company(self, company_id: int, message: dict):#esto envia el mensaje a todo el mundo
        for ws in self.company_connections.get(company_id, []):
            await ws.send_json(message)


    async def send_to_user(self, user_id: int, message: dict):#esto lo envia a un usuario en especifico
        for ws in self.user_connections.get(user_id, []):
            await ws.send_json(message)

manager = ConnectionManager()


#FUNCIONES


async def notify_company_join(request_id: int, session: Session, user: User):

    request = session.query(CompanyJoinRequest).filter(CompanyJoinRequest.id == request_id).first()
    company = request.company

    print(f"🤡🤡🤡🤡🤡🤡 esto es el request_id: {request.id}")

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    owner_id = company.owner_id

    print(f"escribiendo mensaje")
    
    message = {
                "type": "company_join_request",
                "data": {
                        "username": user.username,
                        "user_id": user.id,
                        "company_id": request.company_id,
                        "join_request_id": request.id,
                    },
                "user_id": owner_id                     
}

    print(f"enviando a {owner_id}")
    await create_notification(owner_id, company.id, message, session)


async def create_notification(user_id: int, company_id: int, message: dict, session: Session):

    notification = Notification(
        user_id=user_id,
        company_id=company_id,
        type=message["type"],
        data=message["data"]
    )

    session.add(notification)
    session.commit()
    session.refresh(notification)
    print(f"guardado en la db")

    print(f"conexiones activas: {manager.user_connections}")
    print(f"enviando mensaje pero en create_notification")
    await manager.send_to_user(user_id, {
                                        "id": notification.id,
                                        "type": message["type"],
                                        "data": message["data"]
    })


async def show_notifications(session: Session, user: User):
    #obtener company_id
    company_id = user.company_id

    #obtener notificaciones
    notifications = session.query(Notification).filter(Notification.company_id == company_id).all()

    return notifications