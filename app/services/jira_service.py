import requests
from app.core.config import settings

def get_ticket(ticket_id: str):
    url = f"{settings.JIRA_BASE_URL}/rest/api/2/issue/{ticket_id}"
    auth = (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
    response = requests.get(url, auth=auth)
    return response.json()

def add_comment(ticket_id: str, comment: str):
    url = f"{settings.JIRA_BASE_URL}/rest/api/2/issue/{ticket_id}/comment"
    auth = (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
    payload = {"body": comment}
    response = requests.post(url, json=payload, auth=auth)
    return response.json()
