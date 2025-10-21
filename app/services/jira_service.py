import json
import requests
from requests.auth import HTTPBasicAuth
from app.core.config import settings
from app.services.jira_parser import simplify_jira_issue


def get_ticket(ticket_id: str):
    """
    Fetch a Jira issue using the official Jira Cloud API format.
    Docs: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-get
    """
    url = f"{settings.JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}"
    auth = HTTPBasicAuth(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code != 200:
        print(f"[JIRA ERROR] Failed to fetch ticket {ticket_id}: {response.status_code} {response.text}")
        return {"error": f"Unable to fetch Jira ticket {ticket_id}", "status": response.status_code}

    try:
        data = simplify_jira_issue(response.json())
        return data
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from Jira"}


def add_comment(ticket_id: str, comment: str):
    """
    Add a comment to a Jira issue.
    Docs: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-post
    """
    url = f"{settings.JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/comment"
    auth = HTTPBasicAuth(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "body": comment
    }

    response = requests.post(url, headers=headers, auth=auth, data=json.dumps(payload))

    if response.status_code not in (200, 201):
        print(f"[JIRA ERROR] Failed to post comment on {ticket_id}: {response.status_code} {response.text}")
        return {"error": f"Unable to post comment on Jira ticket {ticket_id}", "status": response.status_code}

    try:
        return response.json()
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from Jira"}




# import requests
# from app.core.config import settings

# def get_ticket(ticket_id: str):
#     url = f"{settings.JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}"
#     auth = (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
#     response = requests.get(url, auth=auth)
#     return response.json()

# def add_comment(ticket_id: str, comment: str):
#     url = f"{settings.JIRA_BASE_URL}/rest/api/3/issue/{ticket_id}/comment"
#     auth = (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
#     payload = {"body": comment}
#     response = requests.post(url, json=payload, auth=auth)
#     return response.json()