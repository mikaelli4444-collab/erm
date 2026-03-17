from fastapi import HTTPException, WebSocket
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
        await websocket.accept() #esto acepta la conexion al servidor

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

async def create_notification(user_id: int, session: Session, message: dict):

    notification = Notification(
        user_id=user_id,
        type=message["type"]
    )

    session.add(notification)
    session.commit()


async def notify_company_join(user: User, session: Session):

    company = session.query(Company).filter(Company.id == user.company_id).first()

    if not company:
        return

    owner_id = company.owner_id

    message = {
        "type": "company_join_request",
        "data": f"{user.username} quiere unirse a la empresa",
        "user_id": owner_id
    }

    await create_notification(owner_id, message, session)

async def send_to_user(self, user_id: int, message: dict):
    ws = self.user_connections.get(user_id)

    if ws:
        try:
            await ws.send_json(message)
        except:
            pass

async def create_notification(user_id: int, company_id: int, message: dict, session: Session):

    notification = Notification(
        user_id=user_id,
        company_id=company_id,
        type=message["type"],
        data=message["data"]
    )

    session.add(notification)
    session.commit()

async def show_notifications(user: User, session: Session):
    #obtener company_id
    company_id = user.company_id

    #obtener notificaciones
    notifications = session.query(Notification).filter(Notification.company_id == company_id).all()

    return notifications