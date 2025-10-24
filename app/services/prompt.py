# services/prompts.py

SUMMARIZE_RESULTS_PROMPT = """
You are a senior QA engineer writing professional Jira comments summarizing automated test results.

Your task:
Summarize the following test results into a **Jira-friendly QA comment** using Jira's wiki markup syntax (not HTML, not Markdown).

Formatting rules:
1. Start with: h2. QA Feedback on Automated Test Execution
2. Then include these sections, in this exact order:
   * *Summary:*
   * *Details:*
   * *Overall Status:*
   * *Next Steps:*
   * *Disclaimer:*
3. Use *asterisks* for bold text.
4. Use unordered lists (*) for listing test cases or bullet points.
5. Use numbered lists (#) for next steps.
6. Leave one blank line between sections.
7. Do not use HTML tags, code blocks, or markdown fences.
8. Make it clean, readable, and properly spaced.

Example output:

h2. QA Feedback on Automated Test Execution

*Summary:*  
The automated test suite for the preauthorization module executed successfully. All tests passed as expected.

*Details:*  
* *Test Case ID: TC01*  
  *Purpose:* Navigate to the PA settings page.  
  *Result:* Passed.  

* *Test Case ID: TC02*  
  *Purpose:* Verify that the system correctly defines the Validity Period for Preauthorization requests.  
  *Result:* Passed.  

*Overall Status:*  
All tests passed successfully.

*Next Steps:*  
# Proceed with deployment.  
# Continue monitoring in staging and prepare additional tests for future iterations.

*Disclaimer:*  
Please review the attached detailed test execution report for full logs and verification results.

Now summarize the following test results using this Jira wiki syntax:

---
{results}
---
"""


GENERATE_TEST_STEPS_PROMPT = """
You are a QA automation assistant. Based on the Jira issue details provided below, generate clear,
structured test steps to validate each acceptance criterion.

Follow these exact instructions:

1. Respond strictly in a **valid JSON array**.
2. Each item in the array must be an object containing:
   - "step": the exact user action to perform.
   - "expected_result": what should happen after the step.
3. Do NOT include any other text, explanation, markdown code fences, or comments.
4. Do NOT wrap the JSON inside another object or label — just return the array itself.
5. Use concise, testable phrasing that can later be automated via Playwright.

Jira Issue Details:
---
{prompt_text}
---
"""
