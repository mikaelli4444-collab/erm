from fastapi import WebSocket, HTTPException
from sqlalchemy.orm import Session
from notification.notification_model import Notification
from users.users_model import User, Company, CompanyJoinRequest
from sqlalchemy import or_



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

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    company = request.company
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    owner_id = company.owner_id

    message = {
                        "type": "company_join_request",
                        "data": {
                                    "username": user.username,
                                    "user_id": user.id,
                                    "company_id": request.company_id,
                                    "join_request_id": request.id,
                            }
                        }
            
    request.message = message
    session.commit()

    print(f"enviando a {owner_id}")
    manager.send_to_user(owner_id, message)


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
    notifications = session.query(Notification).filter(
        or_(
            Notification.company_id == user.company_id,
            Notification.user_id == user.id
        )
    ).all()

    return notifications


async def create_company_notification(user_id: int, message: dict, session: Session):

    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    notification = Notification(
        user_id=user_id,
        company_id=None,
        type=message["type"],
        data=message["data"]            #posiblemente este todo mal aqui, pero lo que quiero hacer es que le llegue una notificacion a un usuario 
    )                                   #que no tenga empresa para avisarle que se tiene que unir a una o crearla el mismo, despues dos botones 
                                        #que digan que quiere crearla y otro que quiere unirse, se le mostrara hasta que forme parte de una empresa
    session.add(notification)
    session.commit()
    session.refresh(notification)

    await manager.send_to_user(user_id, {
                                        "id": notification.id,
                                        "type": message["type"],
                                        "data": message["data"]
    })


async def ensure_company_assignment_reminder(user: User, session: Session):
    if user.company_id is not None:
        return

    notification = session.query(Notification).filter(
        Notification.user_id == user.id,
        Notification.type == "company_assignment_reminder",
        Notification.is_read == False
    ).first()

    if notification:
        return

    message = {
        "type": "company_assignment_reminder",
        "data": {
            "title": "Crea o únete a una empresa",
            "message": "Para usar la app debes crear o unirte a una empresa.",
            "actions": [
                {"label": "Crear empresa", "action": "create_company"},
                {"label": "Unirme a una empresa", "action": "join_company"}
            ]
        }
    }

    await create_company_notification(user.id, message, session)