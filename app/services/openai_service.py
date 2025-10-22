import anyio
from openai import OpenAI
from app.core.config import settings

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_test_steps(prompt_text: str):
    """
    Generate structured QA test steps asynchronously using OpenAI GPT.
    Safe for FastAPI async environment.
    """
    user_prompt = (
        "You are a QA automation assistant. Based on the Jira issue details below, "
        "generate structured, step-by-step test cases that validate each acceptance criterion. "
        "Respond strictly in JSON format with the following fields for each step: "
        "`step` (the action) and `expected_result` (the validation outcome).\n\n"
        f"{prompt_text}"
    )

    def _run_openai_sync():
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert QA tester."},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    # Run in background thread
    return await anyio.to_thread.run_sync(_run_openai_sync)


async def summarize_results(results: str):
    """
    Summarize automated test results asynchronously into a concise Jira-friendly QA comment.
    """
    user_prompt = f"""
    Summarize these automated test results into a concise, professional QA feedback comment for Jira:
    ---
    {results}
    ---
    Include: overall test status, number of passed/failed tests (if mentioned), and next steps if any.
    """

    def _run_openai_sync():
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a senior QA engineer."},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content.strip()

    return await anyio.to_thread.run_sync(_run_openai_sync)





# from openai import OpenAI
# from app.core.config import settings

# # Initialize OpenAI client (new API structure)
# client = OpenAI(api_key=settings.OPENAI_API_KEY)


# def generate_test_steps(prompt_text: str):
#     """
#     Generate structured QA test steps from a given Jira LLM prompt or plain text description.
#     The function expects a complete, contextual Jira issue prompt as returned by jira_service.get_ticket().
#     """
#     user_prompt = (
#         "You are a QA automation assistant. Based on the Jira issue details below, "
#         "generate structured, step-by-step test cases that validate each acceptance criterion. "
#         "Respond strictly in JSON format with the following fields for each step: "
#         "`step` (the action) and `expected_result` (the validation outcome).\n\n"
#         f"{prompt_text}"
#     )

#     response = client.chat.completions.create(
#         model="gpt-4-turbo",
#         messages=[
#             {"role": "system", "content": "You are an expert QA tester."},
#             {"role": "user", "content": user_prompt},
#         ],
#     )

#     return response.choices[0].message.content.strip()


# def summarize_results(results: str):
#     """
#     Summarize automated test execution results into a concise, Jira-friendly QA comment.
#     Compatible with OpenAI Python SDK >= 1.0.0.
#     """
#     user_prompt = f"""
#     Summarize these automated test results into a concise, professional QA feedback comment for Jira:
#     ---
#     {results}
#     ---
#     Include: overall test status, number of passed/failed tests (if mentioned), and next steps if any.
#     """

#     response = client.chat.completions.create(
#         model="gpt-4-turbo",
#         messages=[
#             {"role": "system", "content": "You are a senior QA engineer."},
#             {"role": "user", "content": user_prompt},
#         ],
#     )

#     return response.choices[0].message.content.strip()
