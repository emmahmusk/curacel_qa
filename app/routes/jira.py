from fastapi import APIRouter
from app.services import jira_service

router = APIRouter()

@router.get("/fetch/{ticket_id}")
def fetch_ticket(ticket_id: str):
    """Fetch Jira ticket details."""
    return jira_service.get_ticket(ticket_id)

@router.post("/comment/{ticket_id}")
def post_comment(ticket_id: str, comment: str):
    """Post QA feedback comment to Jira."""
    return jira_service.add_comment(ticket_id, comment)
