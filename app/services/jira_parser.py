import re

def extract_text_from_adf(adf):
    """Recursively extract plain text from Atlassian Document Format (ADF)."""
    if not adf:
        return ""
    text = ""
    if isinstance(adf, dict):
        node_type = adf.get("type")
        if node_type == "text" and "text" in adf:
            text += adf["text"]
        elif "content" in adf:
            for item in adf["content"]:
                text += extract_text_from_adf(item) + "\n"
    elif isinstance(adf, list):
        for item in adf:
            text += extract_text_from_adf(item) + "\n"
    return text.strip()


def extract_acceptance_criteria(adf_content):
    """
    Extract acceptance criteria bullet points from structured Jira ADF description.
    Detects 'Acceptance criteria' heading and collects list items underneath it.
    """
    acceptance_criteria = []
    in_acceptance_section = False

    for node in adf_content:
        node_type = node.get("type")

        # Detect heading that says "Acceptance criteria"
        if node_type == "heading":
            heading_text = "".join(
                c.get("text", "")
                for c in node.get("content", [])
                if isinstance(c, dict) and c.get("type") == "text"
            ).strip().lower()
            in_acceptance_section = "acceptance" in heading_text

        # When in acceptance criteria section, gather bullet list items
        elif in_acceptance_section and node_type == "bulletList":
            for item in node.get("content", []):
                for p in item.get("content", []):
                    for t in p.get("content", []):
                        if "text" in t and t["text"].strip():
                            acceptance_criteria.append(t["text"].strip())

        # Stop if another heading comes after the acceptance section
        elif in_acceptance_section and node_type == "heading":
            break

    # Clean out blanks
    acceptance_criteria = [c for c in acceptance_criteria if c.strip()]
    return acceptance_criteria


def simplify_jira_issue(issue):
    """Convert Jira issue JSON into a flat, LLM-friendly structure."""
    fields = issue.get("fields", {})

    # --- Basic details ---
    summary = fields.get("summary", "")
    status = fields.get("status", {}).get("name", "")
    assignee = (
        fields.get("assignee", {}).get("displayName")
        if fields.get("assignee")
        else "Unassigned"
    )

    # --- Description ---
    raw_description = fields.get("description", {})
    description_content = raw_description.get("content", []) if isinstance(raw_description, dict) else []
    description_text = extract_text_from_adf(raw_description)

    # --- Acceptance Criteria Extraction ---
    acceptance_criteria = extract_acceptance_criteria(description_content)

    # Fallback if structured parsing fails
    if not acceptance_criteria:
        for line in description_text.splitlines():
            if re.search(r"(?i)acceptance criteria", line):
                continue
            if line.strip().startswith(("•", "-", "*", "The ")):
                acceptance_criteria.append(line.strip("-•* ").strip())

    # 🧹 Remove acceptance criteria section from context text to avoid duplication
    context_text = re.split(r"(?i)acceptance criteria", description_text)[0].strip()

    # --- Comments ---
    comments_field = fields.get("comment", {}).get("comments", [])
    comments = [
        extract_text_from_adf(c.get("body", {})).strip()
        for c in comments_field if c.get("body")
    ]
    comments = [c for c in comments if c]  # remove empty strings

    # --- LLM Prompt ---
    acceptance_text = "\n".join(
        [f"- {c}" for c in acceptance_criteria]
    ) if acceptance_criteria else "No explicit acceptance criteria provided."

    comments_text = "\n".join(comments).strip() if comments else "No comments found."

    llm_prompt = f"""
        You are a QA automation assistant.
        Below is a Jira issue summary and its relevant details.

        ---
        **Summary:** {summary}

        **Status:** {status}
        **Assignee:** {assignee}

        **Context & Description:**
        {context_text}

        **Acceptance Criteria:**
        {acceptance_text}

        **Developer Comments:**
        {comments_text}
        ---

        Using the above details, generate automated QA test scenarios that validate each acceptance criterion.
        """.strip()

    # --- Return simplified structure ---
    return {
        "key": issue.get("key"),
        "summary": summary,
        "status": status,
        "assignee": assignee,
        "context": context_text,
        "acceptance_criteria": acceptance_criteria,
        "comments": comments,
        "llm_prompt": llm_prompt,
    }
