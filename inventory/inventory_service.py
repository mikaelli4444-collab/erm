from fastapi import HTTPException, status, WebSocket
from sqlalchemy.orm import Session
from inventory.inventory_model import Inventory, Notification
from inventory.inventory_schema import ItemCreate
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

def create_inventory_item(item_name: str, description: str, quantity: int, session: Session, user: User):
    
    new_item = Inventory(
        item_name=item_name,
        description=description,
        quantity=quantity,
        owner_id=user.id,
        company_id=user.company_id
    )

    session.add(new_item)
    session.commit()
    session.refresh(new_item)

    return {
        "message": "Inventory item created successfully",
        "item": new_item
    }

def edit_inventory_item(item_name: str, item_update: ItemCreate, user: User, session: Session):

    if not user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User not authenticated")
    
    item = session.query(Inventory).filter(Inventory.item_name == item_name, Inventory.company_id == user.company_id).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    item.item_name = item_update.item_name
    item.description = item_update.description
    item.quantity = item_update.quantity
    item.owner_id = user.id

    session.commit()
    session.refresh(item)

    return {
        "message": "Inventory item updated successfully",
        "item": item,
    }

def delete_inventory_item(item_name: str, user: User, session: Session): 
    
    if not user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User not authenticated")

    item_to_delete = session.query(Inventory).filter(Inventory.item_name == item_name, Inventory.company_id == user.company_id).first()

    if not item_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    session.delete(item_to_delete)
    session.commit()

    return {
        "message": "Inventory item deleted successfully",
        "item": item_to_delete
    }

async def notify_company_join(user: User, company: Company, companyjoinrequest: CompanyJoinRequest, session: Session):
    #obtener company_id del user
    user_company_id = user.company_id

    message = {
        "type": "company_join_request",
        "user_id": user.id,
        "username": user.username,
        "company_id": user.company_id
    }

    #obtener empresa y company_owner
    company_obj = session.query(Company).filter(Company.id == user_company_id).first()

    if not company_obj:
        raise HTTPException(status_code=404, detail="Company not found")
    
    owner_id = company_obj.owner_id

    await manager.send_to_user(owner_id, message)

async def send_to_user(self, user_id: int, message: dict):
    ws = self.user_connections.get(user_id)

    if ws:
        try:
            await ws.send_json(message)
        except:
            pass

async def create_notification(user_id: int, message: dict, session: Session):

    notification = Notification(
        user_id=user_id,
        type=message["type"],
        data=str(message["data"])
    )

    session.add(notification)
    session.commit()

    await manager.send_to_user(user_id, message)