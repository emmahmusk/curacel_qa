from fastapi import APIRouter
from app.services import openai_service, ui_validator, jira_service

router = APIRouter()

@router.post("/run-validation/{ticket_id}")
def run_validation(ticket_id: str):
    """
    Fetch Jira ticket → Extract test steps with LLM → Validate via Playwright → Post feedback.
    """
    ticket = jira_service.get_ticket(ticket_id)
    parsed_steps = openai_service.extract_test_steps(ticket["description"])
    results = ui_validator.run_ui_tests(parsed_steps)
    summary = openai_service.summarize_results(results)
    jira_service.add_comment(ticket_id, summary)
    return {"status": "completed", "feedback": summary}
