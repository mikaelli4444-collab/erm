
from pathlib import Path
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from jinja2.exceptions import TemplateNotFound

def use_autorouter(
        router: APIRouter,
        templates:Jinja2Templates, 
        prefix:str = "",
        exclude:list[str]=[]
    ):

    """ Auto router.get for templates """

    @router.get("/{path:path}")
    def autorouter(request:Request, path:str = ""):

        if path.endswith('.html'):
            return RedirectResponse(f"{router.prefix}/{path.removesuffix('.html')}")
        
        if path in exclude:
            raise HTTPException(status_code=404)
        
        # Normalizar: con o sin barra final sirve el mismo template (evita 307)
        if path.endswith("/"):
            path = path.removesuffix("/")

        path = f"{prefix}/{path}.html"

        try:
            print(f"Trying template '{path}'")
            response = templates.TemplateResponse(path, {"request": request})
            return response
        except TemplateNotFound:
            print(f"AutoRouterError: The template '{path}' does not exists.")
            raise HTTPException(status_code=404)
        
        except Exception as e:
            print(f"AutoRouterError: {e}")
            raise HTTPException(status_code=500)
