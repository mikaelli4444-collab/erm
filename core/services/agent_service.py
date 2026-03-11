"""
Executes copilot/agent-decided actions using existing models/services.
Returns a human-readable string. Tools not implemented in backend return a clear "not available" message.
"""
from datetime import date
from sqlalchemy.orm import Session

from contacts.contacts_models import Contacts
from contacts.contacts_services import CreateContact
from contacts.contacts_schema import ContactsBase, types as contact_types
from production.production_model import Production
from users.users_model import User

try:
    from inventory.inventory_model import Inventory
except ImportError:
    Inventory = None


def run_action(tool: str, parameters: dict, session: Session, user: User) -> str:
    if tool == "create_contact":
        return _create_contact(parameters, session, user)
    if tool == "list_contacts":
        return _list_contacts(session)
    if tool == "search_contact":
        return _search_contact(parameters.get("query") or parameters.get("name") or "", session)
    if tool in ("list_production", "list_projects"):
        return _list_production(session)
    if tool == "search_project":
        return _search_production(parameters.get("query") or "", session)
    if tool == "create_project":
        return _create_production(parameters, session)
    if tool in ("app_status", "get_status"):
        return _app_status(session)
    # Inventory
    if tool == "list_inventory_items":
        return _list_inventory(session, user)
    if tool == "count_inventory_items":
        return _count_inventory(session, user, parameters.get("category") or "")
    if tool == "search_inventory_item":
        return _search_inventory(parameters.get("query") or "", session, user)
    if tool == "get_low_stock_items":
        return _low_stock(session, user)
    if tool in ("upload_inventory_file", "import_inventory_items"):
        return _not_available("upload")
    # Finance (no backend yet)
    if tool in ("create_finance_record", "list_finance_records", "get_finance_summary", "sum_finance_by_category", "search_finance_record"):
        return _not_available("finance")
    return f"Unknown action: {tool}"


def _not_available(module: str) -> str:
    return "Esta acción no está disponible aún en el sistema." if module else "Not available."


def _create_contact(params: dict, session: Session, user: User) -> str:
    name = (params.get("name") or "").strip()
    if not name:
        return "Error: name is required to create a contact."
    type_val = (params.get("type") or "client").strip().lower()
    if type_val not in ("architect", "personal", "employed", "client"):
        type_val = "client"
    try:
        contact = ContactsBase(
            name=name,
            email=(params.get("email") or "").strip() or None,
            phone=(params.get("phone") or "").strip() or "-",
            type=getattr(contact_types, type_val, contact_types.client),
        )
        CreateContact(contact, user, session)
        return f"Contact '{name}' created successfully."
    except Exception as e:
        return f"Could not create contact: {str(e)}"


def _list_contacts(session: Session) -> str:
    rows = session.query(Contacts).all()
    if not rows:
        return "No contacts found."
    lines = [f"• {c.name} | {c.email or '-'} | {c.phone} | {c.type}" for c in rows]
    return "Contacts:\n" + "\n".join(lines)


def _search_contact(query: str, session: Session) -> str:
    q = (query or "").strip()
    if not q:
        return "Please provide a search term (e.g. name or email)."
    pattern = f"%{q}%"
    rows = (
        session.query(Contacts)
        .filter((Contacts.name.ilike(pattern)) | (Contacts.email.ilike(pattern)))
        .limit(20)
        .all()
    )
    if not rows:
        return f"No contacts found for '{q}'."
    lines = [f"• {c.name} | {c.email or '-'} | {c.phone} | {c.type}" for c in rows]
    return "Results:\n" + "\n".join(lines)


def _list_production(session: Session) -> str:
    rows = session.query(Production).all()
    if not rows:
        return "No projects in production."
    lines = [
        f"• {p.project_name} | client: {p.client_name} | {p.status} | delivery: {p.delivery_date}"
        for p in rows
    ]
    return "Projects:\n" + "\n".join(lines)


def _app_status(session: Session) -> str:
    try:
        session.query(Contacts).limit(1).first()
    except Exception as e:
        return f"App running. Database: connection error ({e})."
    return "App running. Database: connected."


def _search_production(query: str, session: Session) -> str:
    q = (query or "").strip()
    if not q:
        return "Provide a project name to search."
    pattern = f"%{q}%"
    rows = session.query(Production).filter(Production.project_name.ilike(pattern)).limit(20).all()
    if not rows:
        return f"No projects found for '{q}'."
    lines = [f"• {p.project_name} | client: {p.client_name} | {p.status} | {p.delivery_date}" for p in rows]
    return "Projects:\n" + "\n".join(lines)


def _create_production(params: dict, session: Session) -> str:
    name = (params.get("name") or params.get("project_name") or "").strip()
    if not name:
        return "Error: project name is required."
    client_name = (params.get("client_name") or params.get("client") or "").strip() or "-"
    today = date.today()
    try:
        item = Production(
            project_name=name,
            client_name=client_name,
            delivery_date=today,
            description=(params.get("description") or "").strip() or "-",
            status=(params.get("status") or "pending").strip() or "pending",
        )
        session.add(item)
        session.commit()
        return f"Project '{name}' created successfully."
    except Exception as e:
        session.rollback()
        return f"Could not create project: {str(e)}"


def _list_inventory(session: Session, user: User) -> str:
    if Inventory is None:
        return _not_available("inventory")
    rows = session.query(Inventory).filter(Inventory.owner_id == user.id).all()
    if not rows:
        return "No inventory items."
    lines = [f"• {r.item_name} | {r.description} | qty: {r.quantity}" for r in rows]
    return "Inventory:\n" + "\n".join(lines)


def _count_inventory(session: Session, user: User, category: str) -> str:
    if Inventory is None:
        return _not_available("inventory")
    q = session.query(Inventory).filter(Inventory.owner_id == user.id)
    if category:
        cat = f"%{category}%"
        q = q.filter((Inventory.item_name.ilike(cat)) | (Inventory.description.ilike(cat)))
    n = q.count()
    if category:
        return f"Hay {n} ítem(s) que coinciden con '{category}'."
    return f"Hay {n} ítem(s) en el inventario."


def _search_inventory(query: str, session: Session, user: User) -> str:
    if not (query or "").strip():
        return "Indicá el nombre o descripción a buscar."
    if Inventory is None:
        return _not_available("inventory")
    pattern = f"%{query.strip()}%"
    rows = session.query(Inventory).filter(Inventory.owner_id == user.id).filter((Inventory.item_name.ilike(pattern)) | (Inventory.description.ilike(pattern))).limit(20).all()
    if not rows:
        return f"No hay ítems que coincidan con '{query.strip()}'."
    lines = [f"• {r.item_name} | {r.description} | qty: {r.quantity}" for r in rows]
    return "Resultados:\n" + "\n".join(lines)


def _low_stock(session: Session, user: User, threshold: int = 10) -> str:
    if Inventory is None:
        return _not_available("inventory")
    rows = session.query(Inventory).filter(Inventory.owner_id == user.id, Inventory.quantity <= threshold).all()
    if not rows:
        return f"No hay ítems con stock bajo (umbral: {threshold})."
    lines = [f"• {r.item_name} | {r.description} | qty: {r.quantity}" for r in rows]
    return f"Stock bajo (≤{threshold}):\n" + "\n".join(lines)
