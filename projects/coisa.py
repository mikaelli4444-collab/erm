from datetime import datetime
from zoneinfo import ZoneInfo
import time

def hora():
    time.sleep(1)
    print(datetime.now(ZoneInfo("America/Sao_Paulo")))
    hora()

hora()