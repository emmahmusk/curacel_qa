import anyio
import json
import traceback
import re
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_test_steps(prompt_text: str):
    """
    Generate structured QA test steps asynchronously using OpenAI GPT.
    Ensures clean, consistent JSON output: [{step, expected_result}]
    Automatically flattens nested objects if necessary.
    """
    user_prompt = (
        "You are a QA automation assistant. Based on the Jira issue details below, "
        "generate structured, step-by-step test cases that validate each acceptance criterion. "
        "Respond strictly in JSON array format, where each item is an object containing: "
        "`step` (the action) and `expected_result` (the validation outcome). "
        "Do not wrap it in any other object or text — only valid JSON.\n\n"
        f"{prompt_text}"
    )

    def _run_openai_sync():
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                temperature=0.3,
                max_tokens=800,
                messages=[
                    {"role": "system", "content": "You are an expert QA tester."},
                    {"role": "user", "content": user_prompt},
                ],
            )
            content = response.choices[0].message.content.strip() if response.choices else ""
            if not content:
                raise ValueError("Empty response from OpenAI.")
            return content
        except Exception as e:
            print(f"[OPENAI ERROR] Failed to generate test steps: {e}")
            traceback.print_exc()
            return ""

    raw_output = await anyio.to_thread.run_sync(_run_openai_sync)

    if not raw_output:
        return [{"step": "Failed to generate test steps", "expected_result": "Manual review required"}]

    # --- Clean and parse JSON output ---
    try:
        cleaned = re.sub(r"^```(?:json)?|```$", "", raw_output.strip(), flags=re.IGNORECASE).strip()
        parsed = json.loads(cleaned)

        # Handle nested structures like {"test_cases": [...]}
        if isinstance(parsed, dict):
            if "test_cases" in parsed:
                parsed = parsed["test_cases"]
            elif "steps" in parsed:
                parsed = parsed["steps"]
            elif "step" in parsed and isinstance(parsed["step"], dict) and "test_cases" in parsed["step"]:
                parsed = parsed["step"]["test_cases"]
            else:
                parsed = [parsed]

        # Flatten nested test_case structures
        flattened = []
        for item in parsed:
            if isinstance(item, dict) and "steps" in item:
                flattened.extend(item["steps"])
            elif isinstance(item, dict):
                flattened.append(item)
        return flattened

    except Exception as e:
        print(f"[PARSING ERROR] Could not parse LLM JSON output: {e}")
        traceback.print_exc()
        snippet = raw_output[:300].replace("\n", " ")
        return [{
            "step": "Failed to parse test steps",
            "expected_result": f"Parsing error: {e}. Partial output: {snippet}"
        }]

async def summarize_results(results: str):
    """
    Summarize automated test results into a Jira-friendly, readable QA comment.
    Parses structured test data if present, and formats for Jira wiki markup.
    """
    # Prepare the prompt to force Jira wiki formatting
    user_prompt = f"""
    You are a senior QA automation engineer preparing a Jira comment based on automated test results.

    The Jira comment must:
    - Use **double asterisks** for bold text (Jira wiki markup).
    - Begin with **QA Feedback on Automated Test Execution**
    - Include exactly these sections in this order:
        **Summary:**
        **Details:**
        **Overall Status:**
        **Next Steps:**
        **Disclaimer:**
    - Separate sections with one blank line for readability.
    - In **Details**, include each test case with ID, short purpose, and result.
    - If all test cases passed, mark **Overall Status:** Passed.
      If any failed, mark **Overall Status:** Failed.
    - Keep the tone formal, concise, and professional.
    - End with: 
      "Please review the attached detailed test execution report for full logs and verification results."

    Automated Test Results:
    ---
    {results}
    ---
    """

    def _run_openai_sync():
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                temperature=0.3,
                max_tokens=1200,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior QA automation engineer writing structured Jira comments. "
                            "Use only Jira wiki formatting (no markdown code blocks, no single *). "
                            "Always return double-asterisk bold headings and clean paragraphs."
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ],
            )

            content = response.choices[0].message.content.strip() if response.choices else ""
            if not content:
                raise ValueError("Empty response from OpenAI.")
        except Exception as e:
            print(f"[OPENAI ERROR] Failed to summarize results: {e}")
            traceback.print_exc()
            return (
                "**QA Feedback on Automated Test Execution**\n\n"
                "**Summary:**\nUnable to generate automated summary.\n\n"
                "**Details:**\nInternal processing error.\n\n"
                "**Overall Status:** Failed to generate feedback.\n\n"
                "**Next Steps:**\n- Review raw logs manually.\n- Retry automated execution.\n\n"
                "**Disclaimer:**\nPlease review the attached detailed test report."
            )

        # Cleanup for Jira rendering
        text = content
        text = re.sub(r"[`#_>]+", "", text)  # remove markdown remnants
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        # Ensure double asterisks for Jira bold headers
        text = re.sub(r"(?<!\*)\*(Summary|Details|Overall Status|Next Steps|Disclaimer):(?=\s|$)", r"**\1:**", text)
        text = re.sub(r"(?<!\*)\*QA Feedback on Automated Test Execution\*",
                      r"**QA Feedback on Automated Test Execution**", text)

        # Ensure consistent section spacing
        text = re.sub(r"(?<=\n)(?=\*\*)", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        return text

    return await anyio.to_thread.run_sync(_run_openai_sync)


# async def summarize_results(results: str):
#     """
#     Summarize automated test results into a structured, Jira-friendly comment.
#     Produces *bold* headers (Jira wiki format) with good spacing and clear readability.
#     Automatically detects missing headers and reformats accordingly.
#     """
#     user_prompt = f"""
#     Summarize these automated test results into a professional QA comment for Jira.

#     *Formatting Rules:*
#     - Use Jira-style bold headers with single asterisks (e.g., *Summary:*).
#     - Include exactly three sections:
#       *Summary:*
#       *Detailed Findings:*
#       *Next Steps:*
#     - Separate each section with one blank line.
#     - Keep it descriptive, concise, and clear.
#     - Avoid using markdown code fences, hashes (#), or underscores.
#     - If there is no test failure, explicitly state all tests passed.

#     Test Results:
#     ---
#     {results}
#     ---
#     """

#     def _run_openai_sync():
#         try:
#             response = client.chat.completions.create(
#                 model="gpt-4-turbo",
#                 temperature=0.45,
#                 max_tokens=1000,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": (
#                             "You are a senior QA engineer writing polished Jira comments "
#                             "for automated test runs. Always include all three sections clearly."
#                         ),
#                     },
#                     {"role": "user", "content": user_prompt},
#                 ],
#             )
#             content = response.choices[0].message.content.strip() if response.choices else ""
#             if not content:
#                 raise ValueError("Empty response from OpenAI.")
#         except Exception as e:
#             print(f"[OPENAI ERROR] Failed to summarize results: {e}")
#             traceback.print_exc()
#             return (
#                 "*Summary:*\nAutomated QA summary unavailable.\n\n"
#                 "*Detailed Findings:*\nAn internal error occurred while generating this summary.\n\n"
#                 "*Next Steps:*\nPlease review the raw test logs manually."
#             )

#         # --- Gentle cleanup (don’t strip important structure) ---
#         text = content.replace("**", "*").replace("__", "")
#         text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)  # remove fenced code blocks only
#         text = re.sub(r"\n{3,}", "\n\n", text).strip()

#         # --- Detect section headers or auto-split if missing ---
#         if not re.search(r"(?i)\bsummary\b", text):
#             # No explicit sections found — infer structure automatically
#             paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
#             summary = paragraphs[0] if len(paragraphs) > 0 else "All automated tests executed successfully."
#             findings = paragraphs[1] if len(paragraphs) > 1 else "All test cases passed as expected."
#             next_steps = paragraphs[2] if len(paragraphs) > 2 else "Proceed with deployment and monitor post-release behavior."
#             text = (
#                 f"*Summary:*\n{summary}\n\n"
#                 f"*Detailed Findings:*\n{findings}\n\n"
#                 f"*Next Steps:*\n{next_steps}"
#             )
#             return text.strip()

#         # --- Extract structured sections if they exist ---
#         sections = {"summary": "", "detailed findings": "", "next steps": ""}
#         current = None
#         for line in text.splitlines():
#             match = re.match(r"(?i)^(summary|detailed findings|next steps)[:\s]*", line.strip())
#             if match:
#                 current = match.group(1).lower()
#                 continue
#             elif current:
#                 sections[current] += line.strip() + " "

#         # Fill defaults for any missing parts
#         for k, v in sections.items():
#             if not v.strip():
#                 if k == "summary":
#                     sections[k] = "All automated tests executed successfully."
#                 elif k == "detailed findings":
#                     sections[k] = "All test cases passed without error."
#                 elif k == "next steps":
#                     sections[k] = "Proceed with deployment and continue monitoring system behavior."

#         formatted = (
#             f"*Summary:*\n{sections['summary'].strip()}\n\n"
#             f"*Detailed Findings:*\n{sections['detailed findings'].strip()}\n\n"
#             f"*Next Steps:*\n{sections['next steps'].strip()}"
#         ).strip()

#         # Normalize whitespace
#         formatted = re.sub(r"\s{2,}", " ", formatted)
#         formatted = re.sub(r"\n{3,}", "\n\n", formatted)
#         return formatted

#     return await anyio.to_thread.run_sync(_run_openai_sync)