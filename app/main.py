# import sys
# import asyncio

# # Apply fix for Playwright on Windows (must run BEFORE importing anything that uses asyncio/subprocess)
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from app.routes import jira, qa_agent


app = FastAPI(
    title="Curacel AI QA Agent",
    description="Proof of concept agent that automates Jira QA testing using AI and Playwright.",
    version="1.0.0"
)

# Register routes
app.include_router(jira.router, prefix="/jira", tags=["Jira"])
app.include_router(qa_agent.router, prefix="/qa", tags=["QA Agent"])

@app.get("/")
def home():
    return {"message": "Curacel AI QA Agent is running!"}
