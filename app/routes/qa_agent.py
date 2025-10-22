from fastapi import APIRouter
from app.services import openai_service, ui_validator, jira_service

router = APIRouter()

@router.post("/run-validation/{ticket_id}")
async def run_validation(ticket_id: str):
    """
    Fetch Jira issue → Generate test steps via LLM → Execute UI validation asynchronously →
    Summarize results → Post feedback to Jira.
    """
    # Step 1: Fetch and simplify the Jira issue
    issue = await jira_service.get_ticket(ticket_id)
    if not issue or "llm_prompt" not in issue:
        return {"error": f"Failed to retrieve or parse Jira issue {ticket_id}"}

    # Step 2: Extract test steps from the LLM prompt
    test_steps = await openai_service.generate_test_steps(issue["llm_prompt"])

    # Step 3: Run automated UI validations asynchronously using Playwright
    validation_results = await ui_validator.run_ui_tests(test_steps)

    # Step 4: Summarize results for Jira comment
    summary_comment = await openai_service.summarize_results(validation_results)

    # Step 5: Post summary feedback to Jira
    await jira_service.add_comment(ticket_id, summary_comment)

    # Step 6: Return final structured response
    return {
        "ticket_id": ticket_id,
        "summary": issue.get("summary"),
        "status": "completed",
        "results": validation_results,
        "feedback_posted": summary_comment,
    }
