"""
In-app AI Copilot: CONVERSATION MODE (greetings, help, language) and ACTION MODE (tool calls).
Returns strict JSON only: type, tool, parameters, user_message; clarification includes missing_fields.
Supported languages: Spanish, English, Portuguese (and fr, de, it). Replies in the user's language.
"""
import re
from typing import Any


def _normalize(s: str) -> str:
    return (s or "").strip().lower()


def _extract_kv(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for m in re.finditer(r"(\w+)\s*[=:]\s*([^\s,]+|'[^']*'|\"[^\"]*\")", text, re.I):
        k, v = m.group(1).lower(), m.group(2).strip("'\"")
        out[k] = v
    return out


def _quoted(text: str) -> list[str]:
    return [m[0] or m[1] for m in re.findall(r"'([^']*)'|\"([^\"]*)\"", text)]


def _extract_category(message: str, msg_normalized: str) -> str:
    """Extract category from 'en libros', 'on books', 'cuántos libros hay', 'gasto en libros'."""
    parts = message.strip().split()
    # "cuántos libros hay" / "how many books" → word before "hay" or "there"
    for i, w in enumerate(parts):
        if w.lower().rstrip("?") in ("hay", "there", "loaded") and i >= 1:
            return parts[i - 1].strip().rstrip("?")
        if w.lower() in ("en", "on", "em", "de", "categoría", "category", "categoria") and i + 1 < len(parts):
            return parts[i + 1].strip()
    # last word as category only if not stopword
    stop = ("hay", "?", "inventory", "inventario", "items", "itens", "?")
    if parts and parts[-1].lower().rstrip("?") not in stop:
        return parts[-1].strip().rstrip("?")
    return ""


def _extract_number(message: str):
    """Extract first number from message (e.g. 25000 from 'gasto de 25000')."""
    m = re.search(r"\d+(?:[.,]\d+)?", (message or "").replace(",", "."))
    return m.group(0) if m else None


def _detect_lang(msg: str) -> str:
    """Detecta el idioma del mensaje para responder en el mismo. Fallback: en."""
    m = (msg or "").strip()
    if not m:
        return "en"
    # Por script: cirílico → ru, etc.
    if re.search(r"[\u0400-\u04FF]", m):
        return "ru"
    if re.search(r"[\u4e00-\u9fff]", m):
        return "zh"
    if re.search(r"[\u3040-\u30ff]", m):
        return "ja"
    # Palabras por idioma. Orden: idiomas con palabras más distintivas primero (liste→fr, listar→es/pt, list→en).
    lang_hints = [
        ("es", r"\b(crea|crear|agregar|añadir|mostrame|listar|buscar|qué|podés|estado|borra|contactos|contacto|proyectos|proyecto|necesito|puedes|ayuda|gracias|hola)\b"),
        ("fr", r"\b(crée|créer|ajouter|liste|les |cherche|état|projets|projet|besoin|peux|aide|merci|bonjour)\b"),
        ("pt", r"\b(cria|criar|adicionar|listar|buscar|estado|contatos|contato|projetos|projeto|preciso|pode|ajuda|obrigado|ola)\b"),
        ("de", r"\b(erstell|füg|liste|such|status|kontakte|kontakt|projekte|projekt|brauch|kannst|hilfe|danke|hallo)\b"),
        ("it", r"\b(crea|creare|aggiung|lista|cerca|stato|contatti|contatto|progetti|progetto|serve|puoi|aiuto|grazie|ciao)\b"),
        ("en", r"\b(create|add|list|show|search|status|contacts|contact|projects|project|need|can you|help|thanks|hello)\b"),
    ]
    for code, pattern in lang_hints:
        if re.search(pattern, m, re.I):
            return code
    return "en"


def decide(message: str) -> dict[str, Any]:
    """
    Returns strict JSON-shaped dict:
    type: tool_call | clarification | informational | unsupported
    tool: str | null
    parameters: dict
    user_message: str (natural language reply for the user)
    missing_fields: list[str] (only for clarification)
    """
    msg = _normalize(message)
    if not msg:
        return _informational("help", _help_text("en"), {})

    kv = _extract_kv(message)
    quoted = _quoted(message)
    lang = _detect_lang(message)

    # --- CONVERSATION MODE: greetings ---
    if re.match(r"^(hola|hi|hello|hey|olá|oi|buenos\s+días|good\s+morning|bom\s+dia|buen\s+dia|ciao|bonjour|guten\s+tag)[\s!.]*$", msg):
        return _informational("help", _greeting(lang), {})

    # --- CONVERSATION MODE: "do you speak X?" → reply in that language ---
    if any(x in msg for x in ("can you speak english", "do you speak english", "speak english", "in english")):
        return _informational("help", _speak_lang("en"), {})
    if any(x in msg for x in ("você fala português", "fala português", "fala portugues", "speak portuguese", "em português")):
        return _informational("help", _speak_lang("pt"), {})
    if any(x in msg for x in ("podés hablar en español", "hablar en español", "speak spanish", "en español")):
        return _informational("help", _speak_lang("es"), {})

    # --- CONVERSATION MODE: help / what can you do ---
    if any(x in msg for x in (
        "qué podés", "que podes", "qué puedes", "what can you", "help", "ayuda", "qué hacés",
        "was kannst", "o que pode", "que peux-tu", "cosa puoi", "помощь", "帮助", "何が"
    )):
        return _informational("help", _help_text(lang), {})

    # --- get_status / app status ---
    if any(x in msg for x in (
        "estado del sistema", "estado app", "app status", "system status", "cómo está", "how is the system", "dashboard summary",
        "état du système", "status do sistema", "systemstatus", "stato del sistema"
    )):
        return _tool_call("get_status", {}, _user_msg(lang, "status"))

    # --- list_contacts ---
    if any(x in msg for x in (
        "listar contactos", "mostrar contactos", "ver contactos", "todos los contactos",
        "list contacts", "all contacts", "show contacts",
        "liste les contacts", "liste des contacts", "listar os contactos", "lista contatti", "kontakte auflisten"
    )):
        if "crear" in msg or "add" in msg:
            pass
        else:
            return _tool_call("list_contacts", {}, _user_msg(lang, "list_contacts"))

    # --- search_contact ---
    if any(x in msg for x in ("buscar contacto", "buscar contactos", "find contact", "search contact", "busca a ", "find ")):
        q = kv.get("query") or kv.get("name") or kv.get("q")
        if not q and quoted:
            q = quoted[0]
        if not q:
            # try last word(s) as query
            parts = message.strip().split()
            if len(parts) >= 2 and parts[-1] not in ("contacto", "contactos", "contact"):
                q = parts[-1]
            elif len(parts) >= 3:
                q = " ".join(parts[-2:])
        if q:
            return _tool_call("search_contact", {"query": str(q).strip()}, _user_msg(lang, "search_contact", q=str(q)))
        return _clarification("search_contact", ["query"], _clarify_msg(lang, "search_query"), {})

    # --- create_contact ---
    if any(x in msg for x in ("crear contacto", "crea contacto", "creá contacto", "crea un contacto", "creá un contacto", "agregar contacto", "añadir contacto", "add contact", "create contact", "nuevo contacto")):
        name = (kv.get("name") or kv.get("nombre") or (quoted[0] if quoted else "") or "").strip()
        if not name:
            words = message.strip().split()
            # "contacto para María" / "contact para John" → name = María / John
            for i, w in enumerate(words):
                if w.lower() == "para" and i + 1 < len(words):
                    cand = words[i + 1].strip()
                    if cand.lower() not in ("contacto", "contact", "con", "el", "la", "un", "una", "add", "create"):
                        name = cand
                        break
            if not name:
                for i, w in enumerate(words):
                    if w.lower() in ("llamado", "called", "nombre", "name") and i + 1 < len(words):
                        cand = words[i + 1].strip()
                        if cand.lower() not in ("contacto", "contact", "el", "la", "un", "una"):
                            name = cand
                            break
            if not name and len(words) >= 2:
                for w in words:
                    if w.lower() not in ("crear", "crea", "creá", "agregar", "add", "create", "contacto", "contact", "un", "una", "para"):
                        name = w
                        break
        email = (kv.get("email") or kv.get("mail") or "").strip()
        phone = (kv.get("phone") or kv.get("tel") or kv.get("telefono") or "").strip() or "-"
        type_ = (kv.get("type") or kv.get("tipo") or "client").strip().lower()
        if type_ not in ("architect", "personal", "employed", "client"):
            type_ = "client"

        missing = []
        if not name:
            missing.append("name")
        if not email and "email" not in [f.lower() for f in missing]:
            missing.append("email")

        if missing:
            params_partial = {"name": name} if name else {}
            key = "create_contact_missing_with_name" if name else "create_contact_missing"
            return _clarification("create_contact", missing, _clarify_msg(lang, key, name=name or ""), params_partial)
        return _tool_call("create_contact", {"name": name, "email": email or "-", "phone": phone, "type": type_}, _user_msg(lang, "create_contact", name=name))

    # --- list_projects ---
    if any(x in msg for x in (
        "listar proyectos", "ver proyectos", "listar producción", "proyectos",
        "list projects", "show projects", "liste les projets", "listar os projetos", "lista progetti", "projekte auflisten"
    )):
        if "crear" in msg or "add" in msg:
            pass
        else:
            return _tool_call("list_projects", {}, _user_msg(lang, "list_projects"))

    # --- search_project ---
    if any(x in msg for x in ("buscar proyecto", "search project", "find project", "busca proyecto")):
        q = kv.get("query") or kv.get("name") or (quoted[0] if quoted else "")
        if not q:
            parts = message.strip().split()
            if len(parts) >= 2:
                q = parts[-1] if parts[-1].lower() not in ("proyecto", "project") else (parts[-2] if len(parts) >= 3 else "")
        if q:
            return _tool_call("search_project", {"query": str(q).strip()}, _user_msg(lang, "search_project", q=str(q)))
        return _clarification("search_project", ["query"], _clarify_msg(lang, "search_project_query"), {})

    # --- create_project ---
    if any(x in msg for x in ("crear proyecto", "agregar proyecto", "add project", "create project", "nuevo proyecto")):
        name = (kv.get("name") or kv.get("project_name") or kv.get("proyecto") or (quoted[0] if quoted else "") or "").strip()
        if not name:
            parts = message.strip().split()
            if len(parts) >= 2 and parts[-1].lower() not in ("proyecto", "project"):
                name = parts[-1]
        client = (kv.get("client_name") or kv.get("client") or kv.get("cliente") or "").strip() or "-"
        if not name:
            return _clarification("create_project", ["name"], _clarify_msg(lang, "create_project_name"), {})
        return _tool_call("create_project", {"name": name, "client_name": client}, _user_msg(lang, "create_project", name=name))

    # --- INVENTORY: upload / import (clarification: file_reference) ---
    if any(x in msg for x in ("cargá este archivo", "cargar este archivo", "subir archivo", "upload file", "attach file", "adjuntar archivo", "cargar archivo en inventario", "upload to inventory")):
        return _clarification("upload_inventory_file", ["file_reference"], _clarify_msg(lang, "upload_inventory_file"), {"module": "inventory"})
    if any(x in msg for x in ("importá este excel", "importar excel", "importar este excel", "import excel", "load from file", "cargar excel al inventario", "import to inventory")):
        return _clarification("import_inventory_items", ["file_reference"], _clarify_msg(lang, "import_inventory_file"), {"module": "inventory", "file_type": "excel"})

    # --- INVENTORY: count_inventory_items ---
    if any(x in msg for x in ("cuántos libros", "cuantos libros", "how many books", "how many products", "count inventory", "contar inventario", "cuántos hay", "quantos itens", "count items")):
        category = _extract_category(message, msg)
        return _tool_call("count_inventory_items", {"category": category or ""}, _user_msg(lang, "count_inventory", category=category or "all"))

    # --- INVENTORY: get_low_stock_items ---
    if any(x in msg for x in ("stock bajo", "low stock", "mínimo stock", "minimum stock", "productos que se acaban", "running out", "poco stock", "baixo estoque")):
        return _tool_call("get_low_stock_items", {}, _user_msg(lang, "low_stock"))

    # --- INVENTORY: list / search ---
    if any(x in msg for x in ("listar inventario", "ver inventario", "list inventory", "inventario", "listar itens", "lista do inventário")):
        if "crear" in msg or "add" in msg or "subir" in msg or "import" in msg:
            pass
        else:
            return _tool_call("list_inventory_items", {}, _user_msg(lang, "list_inventory"))
    if any(x in msg for x in ("buscar en inventario", "search inventory", "find item", "buscar item", "buscar producto")):
        q = kv.get("query") or kv.get("q") or (quoted[0] if quoted else "")
        if not q:
            parts = message.strip().split()
            if len(parts) >= 2:
                q = parts[-1] if parts[-1].lower() not in ("inventario", "inventory") else (parts[-2] if len(parts) >= 3 else "")
        if q:
            return _tool_call("search_inventory_item", {"query": str(q).strip()}, _user_msg(lang, "search_inventory", q=str(q)))
        return _clarification("search_inventory_item", ["query"], _clarify_msg(lang, "search_query"), {})

    # --- FINANCE: create_finance_record ---
    if any(x in msg for x in ("registrá un gasto", "registrar gasto", "registrar ingreso", "registrar un gasto", "register expense", "register income", "create finance", "registar despesa", "registar receita")):
        amount = kv.get("amount") or kv.get("monto") or kv.get("valor") or _extract_number(message)
        category = _extract_category(message, msg) or kv.get("category") or kv.get("categoria") or ""
        # don't use number as category
        if category and category.isdigit():
            category = ""
        record_type = "expense" if any(x in msg for x in ("gasto", "expense", "despesa", "gasté", "spent")) else "income"
        if amount is None or amount == "":
            return _clarification("create_finance_record", ["amount"], _clarify_msg(lang, "finance_amount"), {"type": record_type, "category": category})
        return _tool_call("create_finance_record", {"type": record_type, "amount": str(amount), "category": category or "other"}, _user_msg(lang, "create_finance", amount=str(amount), category=category or ""))

    # --- FINANCE: sum_finance_by_category ---
    if any(x in msg for x in ("cuánto gasté", "cuanto gasté", "how much spent", "how much was spent", "sum by category", "total por categoría", "quanto gastei")):
        category = _extract_category(message, msg) or kv.get("category") or ""
        return _tool_call("sum_finance_by_category", {"type": "expense", "category": category or ""}, _user_msg(lang, "sum_finance", category=category or ""))

    # --- FINANCE: get_finance_summary ---
    if any(x in msg for x in ("resumen financiero", "finance summary", "total income", "total expenses", "resumo financeiro", "resumen de este mes", "monthly summary")):
        period = "this_month" if any(x in msg for x in ("este mes", "this month", "este mês")) else ""
        return _tool_call("get_finance_summary", {"period": period or "all"}, _user_msg(lang, "finance_summary"))

    # --- FINANCE: list / search (simple) ---
    if any(x in msg for x in ("listar registros financieros", "list finance", "ver finanzas", "listar finanzas")):
        return _tool_call("list_finance_records", {}, _user_msg(lang, "list_finance"))
    if any(x in msg for x in ("buscar registro financiero", "search finance")):
        q = kv.get("query") or (quoted[0] if quoted else message.strip().split()[-1] if message.strip().split() else "")
        if q:
            return _tool_call("search_finance_record", {"query": str(q)}, _user_msg(lang, "search_finance", q=str(q)))
        return _clarification("search_finance_record", ["query"], _clarify_msg(lang, "search_query"), {})

    # --- unsupported (dangerous or out of scope) ---
    if any(x in msg for x in (
        "borra", "eliminar todo", "delete all", "drop database", "borrar base", "elimina todo",
        "delete the whole database", "delete database", "delete whole database"
    )):
        return _unsupported(_unsupported_msg(lang))

    # default: informational, no action
    return _informational(None, _help_text(lang), {})


def _tool_call(tool: str, parameters: dict, user_message: str) -> dict[str, Any]:
    return {"type": "tool_call", "tool": tool, "parameters": parameters, "user_message": user_message}


def _clarification(tool: str, missing_fields: list[str], user_message: str, parameters: dict | None = None) -> dict[str, Any]:
    return {"type": "clarification", "tool": tool, "missing_fields": missing_fields, "parameters": parameters or {}, "user_message": user_message}


def _informational(tool: str | None, user_message: str, parameters: dict) -> dict[str, Any]:
    return {"type": "informational", "tool": tool or "help", "parameters": parameters, "user_message": user_message}


def _unsupported(user_message: str) -> dict[str, Any]:
    return {"type": "unsupported", "tool": None, "parameters": {}, "user_message": user_message}


# Mensajes por idioma (es, en, pt, fr, de, it). Otros idiomas → en.
HELP = {
    "es": "Puedo ayudarte con contactos, proyectos, inventario, finanzas y estado del sistema.",
    "en": "I can help you with contacts, projects, inventory, finance, and system status.",
    "pt": "Posso ajudar com contactos, projetos, inventário, finanças e estado do sistema.",
    "fr": "Je peux vous aider avec les contacts, projets, inventaire, finance et l'état du système.",
    "de": "Ich kann bei Kontakten, Projekten, Inventar, Finanzen und dem Systemstatus helfen.",
    "it": "Posso aiutarti con contatti, progetti, inventario, finanza e stato del sistema.",
}

USER_MSG = {
    "es": {"list_contacts": "Voy a listar los contactos.", "search_contact": "Voy a buscar el contacto '{q}'.", "create_contact": "Voy a crear el contacto {name}.", "list_projects": "Voy a listar los proyectos.", "search_project": "Voy a buscar el proyecto '{q}'.", "create_project": "Voy a crear el proyecto {name}.", "status": "Voy a consultar el estado del sistema.", "count_inventory": "Voy a contar cuántos hay en el inventario.", "low_stock": "Voy a buscar los productos con stock bajo.", "list_inventory": "Voy a listar el inventario.", "search_inventory": "Voy a buscar '{q}' en el inventario.", "create_finance": "Voy a registrar el movimiento.", "sum_finance": "Voy a calcular cuánto se gastó.", "finance_summary": "Voy a obtener el resumen financiero.", "list_finance": "Voy a listar los registros financieros.", "search_finance": "Voy a buscar en registros financieros."},
    "en": {"list_contacts": "I will list the contacts.", "search_contact": "I will search for contact '{q}'.", "create_contact": "I will create the contact {name}.", "list_projects": "I will list the projects.", "search_project": "I will search for project '{q}'.", "create_project": "I will create the project {name}.", "status": "I will check the system status.", "count_inventory": "I will count inventory items.", "low_stock": "I will get low stock items.", "list_inventory": "I will list inventory items.", "search_inventory": "I will search for '{q}' in inventory.", "create_finance": "I will create the finance record.", "sum_finance": "I will sum by category.", "finance_summary": "I will get the finance summary.", "list_finance": "I will list finance records.", "search_finance": "I will search finance records."},
    "pt": {"list_contacts": "A listar os contactos.", "search_contact": "A buscar o contacto '{q}'.", "create_contact": "A criar o contacto {name}.", "list_projects": "A listar os projetos.", "search_project": "A buscar o projeto '{q}'.", "create_project": "A criar o projeto {name}.", "status": "A verificar o estado do sistema.", "count_inventory": "A contar itens do inventário.", "low_stock": "A buscar itens com estoque baixo.", "list_inventory": "A listar o inventário.", "search_inventory": "A buscar '{q}' no inventário.", "create_finance": "A registrar o movimento.", "sum_finance": "A somar por categoria.", "finance_summary": "A obter o resumo financeiro.", "list_finance": "A listar registros financeiros.", "search_finance": "A buscar nos registros."},
    "fr": {"list_contacts": "Je liste les contacts.", "search_contact": "Je cherche le contact « {q} ».", "create_contact": "Je crée le contact {name}.", "list_projects": "Je liste les projets.", "search_project": "Je cherche le projet « {q} ».", "create_project": "Je crée le projet {name}.", "status": "Je vérifie l'état du système.", "count_inventory": "Je compte les articles.", "low_stock": "Je récupère les articles en rupture.", "list_inventory": "Je liste l'inventaire.", "search_inventory": "Je cherche « {q} ».", "create_finance": "Je crée l'enregistrement.", "sum_finance": "Je fais la somme par catégorie.", "finance_summary": "Je récupère le résumé.", "list_finance": "Je liste les enregistrements.", "search_finance": "Je cherche."},
    "de": {"list_contacts": "Ich liste die Kontakte auf.", "search_contact": "Ich suche den Kontakt '{q}'.", "create_contact": "Ich erstelle den Kontakt {name}.", "list_projects": "Ich liste die Projekte auf.", "search_project": "Ich suche das Projekt '{q}'.", "create_project": "Ich erstelle das Projekt {name}.", "status": "Ich prüfe den Systemstatus.", "count_inventory": "Ich zähle die Artikel.", "low_stock": "Ich hole Artikel mit niedrigem Bestand.", "list_inventory": "Ich liste den Bestand.", "search_inventory": "Ich suche '{q}'.", "create_finance": "Ich erstelle den Eintrag.", "sum_finance": "Ich summiere nach Kategorie.", "finance_summary": "Ich hole die Zusammenfassung.", "list_finance": "Ich liste Finanzeinträge.", "search_finance": "Ich suche."},
    "it": {"list_contacts": "Elencando i contatti.", "search_contact": "Cerco il contatto '{q}'.", "create_contact": "Creo il contatto {name}.", "list_projects": "Elencando i progetti.", "search_project": "Cerco il progetto '{q}'.", "create_project": "Creo il progetto {name}.", "status": "Verifico lo stato del sistema.", "count_inventory": "Conto gli articoli.", "low_stock": "Recupero articoli con stock basso.", "list_inventory": "Elenco l'inventario.", "search_inventory": "Cerco '{q}'.", "create_finance": "Creo il record.", "sum_finance": "Sommo per categoria.", "finance_summary": "Recupero il riepilogo.", "list_finance": "Elenco i record.", "search_finance": "Cerco."},
}

CLARIFY_MSG = {
    "es": {"search_query": "Decime el nombre o email del contacto que querés buscar.", "search_project_query": "Decime el nombre del proyecto a buscar.", "create_contact_missing": "Puedo crear el contacto, pero necesito al menos el email (y nombre).", "create_contact_missing_with_name": "Puedo crear el contacto de {name}, pero necesito al menos el email.", "create_project_name": "Necesito el nombre del proyecto para crearlo.", "upload_inventory_file": "Puedo cargar el archivo en inventario, pero necesito que adjuntes o selecciones el archivo.", "import_inventory_file": "Puedo importar el Excel al inventario, pero necesito el archivo.", "finance_amount": "Necesito el monto para registrar el movimiento."},
    "en": {"search_query": "Please provide the name or email to search for.", "search_project_query": "Please provide the project name to search for.", "create_contact_missing": "I can create the contact, but I need at least the email (and name).", "create_contact_missing_with_name": "I can create the contact for {name}, but I need at least the email.", "create_project_name": "I need the project name to create it.", "upload_inventory_file": "I can upload the file to inventory, but I need you to attach or select the file.", "import_inventory_file": "I can import the Excel to inventory, but I need the file.", "finance_amount": "I need the amount to create the record."},
    "pt": {"search_query": "Indica o nome ou email do contacto a buscar.", "search_project_query": "Indica o nome do projeto a buscar.", "create_contact_missing": "Posso criar o contacto, mas preciso pelo menos do email (e nome).", "create_contact_missing_with_name": "Posso criar o contacto de {name}, mas preciso pelo menos do email.", "create_project_name": "Preciso do nome do projeto para o criar.", "upload_inventory_file": "Posso carregar o ficheiro no inventário, mas preciso que anexe ou selecione o ficheiro.", "import_inventory_file": "Posso importar o Excel para o inventário, mas preciso do ficheiro.", "finance_amount": "Preciso do valor para registar o movimento."},
    "fr": {"search_query": "Indiquez le nom ou l'email du contact à rechercher.", "search_project_query": "Indiquez le nom du projet à rechercher.", "create_contact_missing": "Je peux créer le contact, mais j'ai besoin au moins de l'email (et du nom).", "create_contact_missing_with_name": "Je peux créer le contact pour {name}, mais j'ai besoin au moins de l'email.", "create_project_name": "J'ai besoin du nom du projet pour le créer.", "upload_inventory_file": "Je peux charger le fichier dans l'inventaire, mais il faut joindre ou sélectionner le fichier.", "import_inventory_file": "Je peux importer l'Excel dans l'inventaire, mais j'ai besoin du fichier.", "finance_amount": "J'ai besoin du montant pour enregistrer."},
    "de": {"search_query": "Bitte nennen Sie den Namen oder die E-Mail des gesuchten Kontakts.", "search_project_query": "Bitte nennen Sie den Projektnamen.", "create_contact_missing": "Ich kann den Kontakt anlegen, brauche aber mindestens die E-Mail (und den Namen).", "create_contact_missing_with_name": "Ich kann den Kontakt für {name} anlegen, brauche aber mindestens die E-Mail.", "create_project_name": "Ich brauche den Projektnamen, um es zu erstellen.", "upload_inventory_file": "Ich kann die Datei hochladen, aber Sie müssen die Datei anfügen oder auswählen.", "import_inventory_file": "Ich kann die Excel-Datei importieren, brauche aber die Datei.", "finance_amount": "Ich brauche den Betrag für den Eintrag."},
    "it": {"search_query": "Indica il nome o l'email del contatto da cercare.", "search_project_query": "Indica il nome del progetto da cercare.", "create_contact_missing": "Posso creare il contatto, ma mi serve almeno l'email (e il nome).", "create_contact_missing_with_name": "Posso creare il contatto per {name}, ma mi serve almeno l'email.", "create_project_name": "Mi serve il nome del progetto per crearlo.", "upload_inventory_file": "Posso caricare il file nell'inventario, ma devi allegare o selezionare il file.", "import_inventory_file": "Posso importare l'Excel nell'inventario, ma mi serve il file.", "finance_amount": "Mi serve l'importo per registrare."},
}

UNSUPPORTED_MSG = {
    "es": "Puedo ayudarte con contactos, proyectos y estado de la aplicación, pero no puedo ejecutar esa solicitud.",
    "en": "I can help with contacts, projects, and system status, but I cannot execute that request.",
    "pt": "Posso ajudar com contactos, projetos e estado do sistema, mas não posso executar esse pedido.",
    "fr": "Je peux aider avec les contacts, projets et l'état du système, mais je ne peux pas exécuter cette demande.",
    "de": "Ich kann bei Kontakten, Projekten und dem Systemstatus helfen, aber diese Anfrage kann ich nicht ausführen.",
    "it": "Posso aiutare con contatti, progetti e stato del sistema, ma non posso eseguire questa richiesta.",
}

# Saludo corto para "hola" / "hi" (no repetir la lista entera)
GREETING = {
    "es": "Hola. ¿En qué te puedo ayudar hoy? Podés pedirme contactos, proyectos, inventario, finanzas o el estado del sistema.",
    "en": "Hi. What can I help you with? Ask me about contacts, projects, inventory, finance, or system status.",
    "pt": "Olá. Em que posso ajudar hoje? Pode pedir contactos, projetos, inventário, finanças ou o estado do sistema.",
    "fr": "Bonjour. Comment puis-je vous aider ? Demandez-moi contacts, projets, inventaire, finance ou l'état du système.",
    "de": "Hallo. Womit kann ich helfen? Fragen Sie nach Kontakten, Projekten, Inventar, Finanzen oder Systemstatus.",
    "it": "Ciao. Come posso aiutarti? Chiedimi contatti, progetti, inventario, finanza o stato del sistema.",
}

SPEAK_LANG = {
    "en": "Yes, I can respond in English. I can help you create contacts, list contacts, search contacts, list projects, search projects, and check system status.",
    "es": "Sí, puedo responder en español. Puedo ayudarte a crear contactos, listar contactos, buscar contactos, listar proyectos, buscar proyectos y mostrar el estado del sistema.",
    "pt": "Sim, posso responder em português. Posso ajudar você a criar contatos, listar contatos, buscar contatos, listar projetos, buscar projetos e mostrar o status do sistema.",
    "fr": "Oui, je peux répondre en français. Je peux vous aider avec les contacts, les projets et l'état du système.",
    "de": "Ja, ich kann auf Deutsch antworten. Ich kann bei Kontakten, Projekten und dem Systemstatus helfen.",
    "it": "Sì, posso rispondere in italiano. Posso aiutarti con contatti, progetti e stato del sistema.",
}


def _help_text(lang: str) -> str:
    return HELP.get(lang, HELP["en"])


def _greeting(lang: str) -> str:
    return GREETING.get(lang, GREETING["en"])


def _speak_lang(lang: str) -> str:
    return SPEAK_LANG.get(lang, SPEAK_LANG["en"])


def _user_msg(lang: str, action: str, **kw) -> str:
    d = USER_MSG.get(lang, USER_MSG["en"])
    t = d.get(action, d.get("list_contacts", ""))
    safe = {"q": kw.get("q", ""), "name": kw.get("name", ""), "category": kw.get("category", ""), "amount": kw.get("amount", "")}
    return t.format(**safe) if isinstance(t, str) else str(t)


def _clarify_msg(lang: str, key: str, **kw) -> str:
    d = CLARIFY_MSG.get(lang, CLARIFY_MSG["en"])
    t = d.get(key, d.get("create_contact_missing", "Please provide the missing information."))
    return t.format(name=kw.get("name", "")) if isinstance(t, str) and "{name}" in t else t


def _unsupported_msg(lang: str) -> str:
    return UNSUPPORTED_MSG.get(lang, UNSUPPORTED_MSG["en"])
