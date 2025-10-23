import anyio
import json
import re
import traceback
from openai import OpenAI
from app.core.config import settings
from .prompt import SUMMARIZE_RESULTS_PROMPT, GENERATE_TEST_STEPS_PROMPT

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_test_steps(prompt_text: str):
    """
    Generate structured QA test steps asynchronously using OpenAI GPT.
    Ensures output is valid JSON list of {step, expected_result}.
    """
    user_prompt = GENERATE_TEST_STEPS_PROMPT.format(prompt_text=prompt_text)

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

    try:
        cleaned = re.sub(r"^```(?:json)?|```$", "", raw_output.strip(), flags=re.IGNORECASE).strip()
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            if "test_cases" in parsed:
                parsed = parsed["test_cases"]
            elif "steps" in parsed:
                parsed = parsed["steps"]
            else:
                parsed = [parsed]
        return parsed
    except Exception as e:
        print(f"[PARSING ERROR] Invalid JSON: {e}")
        snippet = raw_output[:300].replace("\n", " ")
        return [{
            "step": "Failed to parse test steps",
            "expected_result": f"Parsing error: {e}. Partial output: {snippet}"
        }]


def convert_text_to_adf(text: str):
    """
    Convert structured plain text QA summary into rich, readable Jira ADF JSON.
    Adds real paragraph spacing, bold headings, subheadings per test case, and emoji indicators.
    """
    import re

    def paragraph(txt):
        return {"type": "paragraph", "content": [{"type": "text", "text": txt.strip()}]}

    def bold_heading(txt, level=3):
        return {
            "type": "heading",
            "attrs": {"level": level},
            "content": [{"type": "text", "text": txt.strip()}],
        }

    def bullet_item(txt):
        return {
            "type": "listItem",
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": txt.strip()}]}],
        }

    def add_spacer(content):
        content.append({"type": "paragraph", "content": []})  # visual line break

    content = []

    # Add main title
    content.append({
        "type": "heading",
        "attrs": {"level": 2},
        "content": [{"type": "text", "text": "QA Feedback on Automated Test Execution"}],
    })
    add_spacer(content)

    # --- Split sections ---
    sections = re.split(r"(?i)(?=summary:|details:|overall status:|next steps:|disclaimer:)", text)
    parsed = {s.split(":", 1)[0].strip().lower(): s.split(":", 1)[1].strip() for s in sections if ":" in s}

    # --- Summary ---
    if "summary" in parsed:
        content.append(bold_heading("Summary", level=3))
        content.append(paragraph(parsed["summary"]))
        add_spacer(content)

    # --- Details ---
    if "details" in parsed:
        content.append(bold_heading("Detailed Test Case Results", level=3))
        add_spacer(content)

        details = parsed["details"]
        # Split each test case cleanly
        test_cases = [t.strip() for t in re.split(r"Test Case ID:", details) if t.strip()]
        for i, case in enumerate(test_cases, start=1):
            lines = [l.strip() for l in case.split(". ") if l.strip()]
            tc_id_match = re.match(r"(TC\d+)", lines[0]) if lines else None
            tc_id = tc_id_match.group(1) if tc_id_match else f"Case {i}"

            # Create subheading for each case
            content.append(bold_heading(f"Test Case {i}: {tc_id}", level=4))

            # Extract purpose and result
            purpose = next((l for l in lines if l.lower().startswith("purpose:")), None)
            result = next((l for l in lines if l.lower().startswith("result:")), None)

            # Build bullets
            bullets = {"type": "bulletList", "content": []}
            if purpose:
                bullets["content"].append(bullet_item(purpose))
            if result:
                emoji = "✅" if "pass" in result.lower() else "❌"
                bullets["content"].append(bullet_item(f"{emoji} {result}"))
            content.append(bullets)
            add_spacer(content)

    # --- Overall Status ---
    if "overall status" in parsed:
        content.append(bold_heading("Overall Status", level=3))
        status_text = parsed["overall status"]
        emoji = "✅" if "pass" in status_text.lower() else "❌"
        content.append(paragraph(f"{emoji} {status_text}"))
        add_spacer(content)

    # --- Next Steps ---
    if "next steps" in parsed:
        content.append(bold_heading("Next Steps", level=3))
        steps = [s.strip() for s in re.split(r"(?<=[.])\s+", parsed["next steps"]) if s.strip()]
        bullet_block = {"type": "bulletList", "content": [bullet_item(s) for s in steps]}
        content.append(bullet_block)
        add_spacer(content)

    # --- Disclaimer ---
    if "disclaimer" in parsed:
        content.append(bold_heading("Disclaimer", level=3))
        content.append(paragraph(parsed["disclaimer"]))
    adf_comment = {"type": "doc", "version": 1, "content": content}
    return adf_comment




async def summarize_results(results: str):
    """
    Summarize automated test results and return ADF JSON for Jira Cloud REST API.
    """
    user_prompt = SUMMARIZE_RESULTS_PROMPT.format(results=results)

    def _run_openai_sync():
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                temperature=0.4,
                max_tokens=1500,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior QA engineer writing professional Jira summaries. "
                            "Output structured plain text with sections: Summary, Details, Overall Status, "
                            "Next Steps, and Disclaimer. Do NOT use HTML, Markdown, or Jira wiki markup."
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
            content = (
                "Summary: Automated QA summary unavailable.\n"
                "Details: An internal error occurred while generating this summary.\n"
                "Overall Status: Failed to generate feedback.\n"
                "Next Steps: Review raw logs manually and retry automated execution.\n"
                "Disclaimer: Please refer to the attached test report for full details."
            )

        # Clean response
        text = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        text = re.sub(r"[#*_`>]+", "", text)
        text = re.sub(r"\s{2,}", " ", text)
        text = text.strip()

        return text

    plain_text = await anyio.to_thread.run_sync(_run_openai_sync)

    # Convert plain text to ADF JSON
    adf_comment = convert_text_to_adf(plain_text)
    return adf_comment
