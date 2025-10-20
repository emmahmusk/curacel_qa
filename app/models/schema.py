from pydantic import BaseModel

class JiraTicket(BaseModel):
    id: str
    description: str

class TestResult(BaseModel):
    step: str
    status: str
    error: str | None = None
