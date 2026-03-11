from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from core.dependencies import CreateSession, templates
from core.security import verify_token
from core.copilot import decide as copilot_decide
from core.services.agent_service import run_action
from core.schemas.agent import ChatRequest, ChatResponse
from users.users_model import User

agent_router = APIRouter(prefix="/agent", tags=["agent"])

COPILOT_TOOLS = {
    "create_contact", "list_contacts", "search_contact",
    "create_project", "list_projects", "search_project",
    "list_inventory_items", "count_inventory_items", "search_inventory_item", "get_low_stock_items",
    "upload_inventory_file", "import_inventory_items",
    "create_finance_record", "list_finance_records", "get_finance_summary", "sum_finance_by_category", "search_finance_record",
    "get_status",
}


@agent_router.get("")
def agent_page(request: Request, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    return templates.TemplateResponse(
        "agent/agent.html",
        {"request": request, "user": user},
    )


@agent_router.post("/chat", response_model=ChatResponse)
def agent_chat(
    body: ChatRequest,
    session: Session = Depends(CreateSession),
    user: User = Depends(verify_token),
):
    decision = copilot_decide(body.message.strip())
    dtype = decision.get("type")
    user_message = decision.get("user_message") or ""

    if dtype == "tool_call":
        tool = decision.get("tool")
        params = decision.get("parameters") or {}
        if tool not in COPILOT_TOOLS:
            return ChatResponse(message=user_message, success=True)
        try:
            result = run_action(tool, params, session, user)
            return ChatResponse(message=f"{user_message}\n\n{result}", success=True)
        except Exception as e:
            return ChatResponse(message=f"{user_message}\n\nError: {str(e)}", success=False)

    return ChatResponse(message=user_message, success=True)
