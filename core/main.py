#uvicorn core.main:app --reload para rodar o app
#uvicorn main:app --reload --log-level debug para debugar cuando el log del error no es tan claro
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from users.users_route import home_router 
from inventory.inventory_route import inventory_router
from production.production_route import production_router
from contacts.contacts_route import contacts_router
from notification.notification_route import notification_router
from notification.ws_route import ws_route
from financery.financery_route import financery_router
from projects.projects_route import projects_router
from payments.payments_router import payments_router
from core.database import base, engine
from core.dependencies import templates


app = FastAPI()

base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
    "home/home.html",
    {"request": request}
    )


app.include_router(home_router)
app.include_router(inventory_router)
app.include_router(production_router)
app.include_router(contacts_router)
app.include_router(notification_router)
app.include_router(ws_route)
app.include_router(financery_router)
app.include_router(projects_router)
app.include_router(payments_router)

for r in app.routes:
    print(r.path)