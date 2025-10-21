import openai
from app.core.config import settings
from app.services.jira_parser import simplify_jira_issue

openai.api_key = settings.OPENAI_API_KEY


def extract_test_steps_from_issue(issue_json: dict):
    """
    Fetches structured context from a Jira issue using the parser,
    and generates automated QA test steps using OpenAI GPT.
    """
    simplified = simplify_jira_issue(issue_json)
    llm_prompt = simplified["llm_prompt"]

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an expert QA tester."},
            {
                "role": "user",
                "content": (
                    "You are a QA automation assistant. Based on the Jira issue details below, "
                    "generate structured, step-by-step test cases that validate each acceptance criterion. "
                    "Respond strictly in JSON with the following fields for each step: "
                    "`step` (the action) and `expected_result` (the validation outcome).\n\n"
                    f"{llm_prompt}"
                ),
            },
        ],
    )

    simplified["generated_tests"] = response.choices[0].message.content
    return simplified


def extract_test_steps(ticket_description: str):
    """
    Legacy version: still usable when you only have plain text description.
    """
    prompt = f"""
    You are a QA automation assistant. Extract structured test steps from this Jira ticket description:
    ---
    {ticket_description}
    ---
    Output in JSON format with fields: step, expected_result.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an expert QA tester."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def summarize_results(results: str):
    """
    Summarizes automated test execution results into a concise, Jira-friendly QA comment.
    """
    prompt = f"""
    Summarize these automated test results into a concise, professional QA feedback comment for Jira:
    ---
    {results}
    ---
    Include: overall test status, number of passed/failed tests (if mentioned), and next steps if any.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a senior QA engineer."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content
