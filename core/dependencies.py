from core.database import SessionLocal
from fastapi.templating import Jinja2Templates
from core.config.config_loader import RAW_CONFIG
from utilities.storage.storage_service import StorageService

def CreateSession():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="frontend/templates")

def get_storage_service():
    return StorageService(RAW_CONFIG.storage)