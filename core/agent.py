"""
Agente que interpreta mensajes del usuario y devuelve la herramienta y parámetros a ejecutar.
Solo mapea a herramientas existentes en el backend (users, contacts, production, inventory).
Si en config hay agent.llm.api_key, usa el LLM para mejorar la detección de intención.
"""
import json
import re
from typing import Any

# Herramientas reales del sistema (según routes)
TOOLS = {
    "create_user": {"params": ["fullname", "username", "email", "password"]},
    "login": {"params": ["username", "password"]},
    "create_contact": {"params": ["name", "email", "phone", "type"]},
    "list_contacts": {"params": []},
    "search_contact": {"params": ["query"]},
    "create_production": {"params": ["project_name", "client_name", "description", "delivery_date", "status"]},
    "list_production": {"params": []},
    "delete_production": {"params": ["project_name"]},
    "create_inventory_item": {"params": ["item_name", "description", "quantity"]},
    "list_inventory": {"params": []},
    "edit_inventory_item": {"params": ["item_name", "item_name_new", "description", "quantity"]},
    "delete_inventory_item": {"params": ["item_name"]},
    "verify_email": {"params": ["code", "verification_jwt"]},
    "refresh_token": {"params": []},
    "app_status": {"params": []},
}

TOOLS_LIST = ", ".join(TOOLS.keys())


def _get_llm_config() -> tuple[str, str]:
    """Lee api_key y model de config. Si no hay agent.llm, devuelve ("", model_por_defecto)."""
    try:
        from core.config.config_loader import RAW_CONFIG
        agent = getattr(RAW_CONFIG, "agent", None)
        llm = getattr(agent, "llm", None) if agent else None
        if not llm:
            return "", "gpt-4o-mini"
        api_key = (getattr(llm, "api_key", None) or "").strip()
        model = getattr(llm, "model", None) or "gpt-4o-mini"
        return api_key, model
    except Exception:
        return "", "gpt-4o-mini"


def _decide_with_llm(message: str, api_key: str, model: str) -> dict[str, Any] | None:
    """Usa el LLM para devolver tool + parameters. Si falla o tool no válida, devuelve None."""
    if not api_key or not message.strip():
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        system = f"""Eres un agente que mapea mensajes del usuario a UNA herramienta del backend.
Herramientas permitidas (solo estas): {TOOLS_LIST}.
Para cada herramienta los parámetros están en TOOLS (no inventes otros).
Responde ÚNICAMENTE con un JSON válido, sin markdown ni texto extra:
{{"tool": "nombre_herramienta", "parameters": {{...}}}}
Si la intención no coincide con ninguna herramienta: {{"tool": "none", "message": "Action not supported."}}
Extrae del mensaje los valores para cada parámetro de la herramienta; si no hay valor usa ""."""
        r = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": message.strip()},
            ],
            max_tokens=400,
        )
        text = (r.choices[0].message.content or "").strip()
        # quitar posibles bloques markdown
        if "```" in text:
            for part in text.split("```"):
                if part.strip().startswith("{"):
                    text = part.strip()
                    break
        data = json.loads(text)
        tool = data.get("tool")
        if tool == "none":
            return {"tool": "none", "message": data.get("message", "Action not supported.")}
        if tool not in TOOLS:
            return None
        params = data.get("parameters") or {}
        if not isinstance(params, dict):
            params = {}
        return {"tool": tool, "parameters": {k: str(v) for k, v in params.items()}}
    except Exception:
        return None


def _normalize(text: str) -> str:
    return (text or "").strip().lower()


def _extract_kv(msg: str) -> dict[str, str]:
    """Extrae pares clave=valor o clave: valor del mensaje."""
    out: dict[str, str] = {}
    for m in re.finditer(r"(\w+)\s*[=:]\s*([^\s,]+|'[^']*'|\"[^\"]*\")", msg, re.I):
        k, v = m.group(1).lower(), m.group(2).strip("'\"")
        out[k] = v
    return out


def _extract_quoted(s: str) -> list[str]:
    return re.findall(r"'([^']*)'|\"([^\"]*)\"", s)


def _decide_keywords(message: str) -> dict[str, Any]:
    """Detección por palabras clave (fallback sin LLM)."""
    msg = _normalize(message)
    kv = _extract_kv(message)
    quoted = _extract_quoted(message)

    # create user / signup / registrar usuario
    if any(x in msg for x in ("crear usuario", "registrar", "signup", "sign up", "alta usuario", "nuevo usuario")):
        return {
            "tool": "create_user",
            "parameters": {
                "fullname": kv.get("fullname") or kv.get("nombre") or (quoted[0][0] or quoted[0][1] if quoted else ""),
                "username": kv.get("username") or kv.get("user") or (quoted[1][0] or quoted[1][1] if len(quoted) > 1 else ""),
                "email": kv.get("email") or (quoted[0][0] or quoted[0][1] if quoted else ""),
                "password": kv.get("password") or kv.get("pass") or "",
            },
        }

    # login / iniciar sesión
    if any(x in msg for x in ("login", "iniciar sesión", "iniciar sesion", "loguear", "entrar")):
        return {
            "tool": "login",
            "parameters": {
                "username": kv.get("username") or kv.get("user") or (quoted[0][0] or quoted[0][1] if quoted else ""),
                "password": kv.get("password") or kv.get("pass") or "",
            },
        }

    # list contacts / listar contactos
    if any(x in msg for x in ("listar contactos", "ver contactos", "contactos", "get_contacts", "list contacts")):
        if "crear" in msg or "add" in msg or "nuevo" in msg:
            pass  # no es list, puede ser create_contact
        else:
            return {"tool": "list_contacts", "parameters": {}}

    # search contact
    if any(x in msg for x in ("buscar contacto", "search contact", "find contact", "buscar contactos")):
        q = kv.get("query") or kv.get("name") or kv.get("q") or (quoted[0][0] or quoted[0][1] if quoted else "")
        return {"tool": "search_contact", "parameters": {"query": q}}

    # create contact
    if any(x in msg for x in ("crear contacto", "añadir contacto", "add contact", "nuevo contacto")):
        return {
            "tool": "create_contact",
            "parameters": {
                "name": kv.get("name") or kv.get("nombre") or (quoted[0][0] or quoted[0][1] if quoted else ""),
                "email": kv.get("email") or "",
                "phone": kv.get("phone") or kv.get("tel") or "",
                "type": kv.get("type") or kv.get("tipo") or "other",
            },
        }

    # list production / list projects
    if any(x in msg for x in ("listar producción", "listar produccion", "ver producción", "list projects", "production", "proyectos producción", "show projects")):
        if "crear" in msg or "add" in msg or "eliminar" in msg or "delete" in msg:
            pass
        else:
            return {"tool": "list_production", "parameters": {}}

    # create production
    if any(x in msg for x in ("crear proyecto producción", "crear production", "add production", "nuevo proyecto producción")):
        return {
            "tool": "create_production",
            "parameters": {
                "project_name": kv.get("project_name") or kv.get("proyecto") or "",
                "client_name": kv.get("client_name") or kv.get("cliente") or "",
                "description": kv.get("description") or kv.get("descripcion") or "",
                "delivery_date": kv.get("delivery_date") or kv.get("fecha_entrega") or "",
                "status": kv.get("status") or kv.get("estado") or "pending",
            },
        }

    # delete production
    if any(x in msg for x in ("eliminar proyecto", "borrar proyecto", "delete production", "delete_production")):
        return {
            "tool": "delete_production",
            "parameters": {"project_name": kv.get("project_name") or kv.get("proyecto") or (quoted[0][0] or quoted[0][1] if quoted else "")},
        }

    # list inventory / inventario / dashboard
    if any(x in msg for x in ("listar inventario", "ver inventario", "inventario", "list inventory", "dashboard inv")):
        if "crear" in msg or "add" in msg or "editar" in msg or "eliminar" in msg:
            pass
        else:
            return {"tool": "list_inventory", "parameters": {"search": kv.get("search") or kv.get("buscar") or ""}}

    # create inventory item
    if any(x in msg for x in ("crear item inventario", "añadir item", "add inventory", "nuevo item inventario")):
        return {
            "tool": "create_inventory_item",
            "parameters": {
                "item_name": kv.get("item_name") or kv.get("nombre") or (quoted[0][0] or quoted[0][1] if quoted else ""),
                "description": kv.get("description") or kv.get("descripcion") or "",
                "quantity": kv.get("quantity") or kv.get("cantidad") or "0",
            },
        }

    # edit inventory item
    if any(x in msg for x in ("editar item", "actualizar item", "edit inventory", "update inventory")):
        return {
            "tool": "edit_inventory_item",
            "parameters": {
                "item_name": kv.get("item_name") or kv.get("item") or (quoted[0][0] or quoted[0][1] if quoted else ""),
                "item_name_new": kv.get("item_name_new") or kv.get("nombre_nuevo") or "",
                "description": kv.get("description") or "",
                "quantity": kv.get("quantity") or "",
            },
        }

    # delete inventory item
    if any(x in msg for x in ("eliminar item inventario", "borrar item", "delete inventory", "delete_inventory_item")):
        return {
            "tool": "delete_inventory_item",
            "parameters": {"item_name": kv.get("item_name") or kv.get("item") or (quoted[0][0] or quoted[0][1] if quoted else "")},
        }

    # verify email
    if any(x in msg for x in ("verificar email", "verify email", "verificar correo", "código verificación")):
        return {
            "tool": "verify_email",
            "parameters": {
                "code": kv.get("code") or kv.get("codigo") or "",
                "verification_jwt": kv.get("verification_jwt") or kv.get("jwt") or "",
            },
        }

    # refresh token
    if any(x in msg for x in ("refresh token", "refrescar token", "renovar token")):
        return {"tool": "refresh_token", "parameters": {}}

    # app / system status
    if any(x in msg for x in ("system status", "estado del sistema", "app status", "show status", "estado app", "status")):
        return {"tool": "app_status", "parameters": {}}

    # list users / tasks / query database → no existen
    if any(x in msg for x in ("listar usuarios", "list users", "crear tarea", "listar tareas", "tasks", "query database", "consultar base")):
        return {"tool": "none", "message": "Action not supported."}

    return {"tool": "none", "message": "Action not supported."}


def decide(message: str) -> dict[str, Any]:
    """
    Interpreta el mensaje y devuelve herramienta y parámetros en JSON.
    Si está configurada agent.llm.api_key, usa el LLM; si no o falla, usa detección por palabras clave.
    Si no hay herramienta válida: {"tool": "none", "message": "..."}.
    """
    api_key, model = _get_llm_config()
    if api_key:
        llm_result = _decide_with_llm(message, api_key, model)
        if llm_result is not None:
            return llm_result
    return _decide_keywords(message)
