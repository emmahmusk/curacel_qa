import openai
from app.core.config import settings

openai.api_key = settings.OPENAI_API_KEY

def extract_test_steps(ticket_description: str):
    prompt = f"""
    You are a QA automation assistant. Extract structured test steps from this Jira ticket description:
    ---
    {ticket_description}
    ---
    Output in JSON format with fields: step, expected_result.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are an expert QA tester."},
                  {"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def summarize_results(results):
    prompt = f"""
    Summarize these test results into a concise Jira QA comment:
    {results}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
