# 🤖 Curacel AI QA Agent  
**AI-powered automation for validating Jira tickets on Curacel’s development environment**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)  
[![FastAPI](https://img.shields.io/badge/FastAPI-Framework-success.svg)](https://fastapi.tiangolo.com/)  
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-lightgrey.svg)](https://openai.com)  
[![Playwright](https://img.shields.io/badge/Automation-Playwright-green.svg)](https://playwright.dev/)  

---

## 🧩 Overview

This project was developed as part of the **Curacel Engineering Trial** — *“See If We Can Work Together”*.  

The goal is to build a **proof-of-concept QA automation agent** that uses **AI (LLMs)** and **UI automation** to validate Jira tickets in the **“QA on Dev”** stage.  

The agent intelligently reviews Jira ticket details, generates relevant validation steps, executes them automatically on the Curacel Dev environment (`https://dev.claims.curacel.co`), and posts summarized QA feedback directly back to Jira.

---

## 🧠 Core Objectives

| # | Objective | Description |
|---|------------|-------------|
| 1 | **Ticket Review** | Fetch and analyze Jira ticket details (description, acceptance criteria, expected behavior). |
| 2 | **AI-Driven Validation** | Use OpenAI’s GPT model to generate validation steps dynamically. |
| 3 | **UI Testing** | Perform automated end-to-end tests on Curacel’s dev environment using Playwright. |
| 4 | **Feedback Automation** | Post concise, actionable QA feedback as comments on the Jira ticket. |
| 5 | **Extra Credit** | Extend validation to include API-level tests (optional). |

---

## 🏗️ System Architecture

```
┌──────────────────────┐
│      Jira Ticket      │
│ (Description, Criteria)│
└──────────┬────────────┘
           │
           ▼
┌────────────────────────┐
│     LLM Parser (GPT-4) │
│ Extract test scenarios │
└──────────┬─────────────┘
           │
           ▼
┌────────────────────────┐
│   UI Validator (Playwright) │
│ Executes test scenarios  │
└──────────┬──────────────┘
           │
           ▼
┌────────────────────────┐
│   QA Feedback Generator │
│  Summarizes & posts back│
└────────────────────────┘
```

### 🧩 Components
- **FastAPI Backend** – orchestrates the process  
- **Jira Service** – handles Jira API operations (fetch, comment)  
- **OpenAI Service** – interprets and summarizes ticket information  
- **UI Validator** – executes browser tests on Curacel’s dev site  
- **Schema Models** – ensure structured communication between modules  

---

## ⚙️ Technology Stack

| Category | Tool / Library |
|-----------|----------------|
| **Framework** | [FastAPI](https://fastapi.tiangolo.com) |
| **Language** | Python 3.10+ |
| **AI Integration** | OpenAI GPT-4 |
| **Automation** | Playwright |
| **Ticket System API** | Jira REST API |
| **Config Management** | python-dotenv |
| **HTTP Requests** | requests |
| **Data Models** | Pydantic |

---

## 🧰 Project Structure

```
curacel_ai_agent/
│
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── routes/                 # HTTP route definitions
│   │   ├── jira_routes.py
│   │   └── qa_agent_routes.py
│   ├── services/               # Business logic
│   │   ├── jira_service.py
│   │   ├── openai_service.py
│   │   └── ui_validator.py
│   ├── models/                 # Pydantic schemas
│   │   └── schemas.py
│   └── core/
│       └── config.py           # Environment variables & settings
│
├── tests/                      # (Optional) Unit & integration tests
├── .env                        # Local environment configuration
├── requirements.txt
├── run.sh
└── README.md
```

---

## ⚡ Quick Start Guide

### 1️⃣ Clone Repository
```bash
git clone https://github.com/<your-username>/curacel-ai-qa-agent.git
cd curacel-ai-qa-agent
```

### 2️⃣ Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
playwright install
```

### 4️⃣ Configure Environment Variables
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key
JIRA_API_TOKEN=your_jira_api_token
JIRA_BASE_URL=https://curacel.atlassian.net
JIRA_EMAIL=youremail@curacel.ai
```

### 5️⃣ Run the Application
```bash
bash run.sh
```

Once running, access the API documentation at:  
👉 **http://127.0.0.1:8000/docs**

---

## 🧪 Example API Endpoints

### ▶️ Fetch a Jira Ticket
```bash
GET /jira/fetch/ENGR-1234
```
Fetches and returns ticket details such as summary, description, and acceptance criteria.

---

### ▶️ Run Full QA Validation
```bash
POST /qa/run-validation/CUR-1234
```
Performs the complete process:
1. Fetch Jira ticket  
2. Extract test scenarios via LLM  
3. Execute UI validation on Curacel Dev  
4. Post QA feedback back to Jira  

**Sample Response:**
```json
{
  "status": "completed",
  "feedback": "All acceptance criteria passed successfully."
}
```

---

## 🧠 AI Workflow Logic

1. **Prompt Construction:**  
   The LLM is given the Jira ticket’s description and acceptance criteria.  
2. **Test Extraction:**  
   GPT-4 converts these into structured, actionable test steps.  
3. **Test Execution:**  
   The UI validator runs the generated steps using Playwright.  
4. **Result Summarization:**  
   The AI summarizes pass/fail results into a concise Jira comment.  

---

## 🧭 Future Enhancements

✅ Add **API-level validations** for bonus points  
✅ Extend support for **multi-ticket processing**  
✅ Implement **asynchronous task queue** (Celery or BackgroundTasks)  
✅ Improve **error handling and reporting**  
✅ Add **Dockerfile** for containerized deployment  

---

## 🧑‍💻 Local Development Notes

| Command | Description |
|----------|-------------|
| `uvicorn app.main:app --reload` | Run app locally |
| `pytest` | Run unit tests (if added) |
| `black .` | Format code |
| `playwright codegen https://dev.claims.curacel.co` | Generate UI actions interactively |

---

## 📈 Evaluation Alignment

| Rubric | How This Project Demonstrates It |
|--------|----------------------------------|
| **Problem Understanding** | Clear end-to-end Jira–AI–Automation workflow design |
| **Solution Design & Approach** | Modular FastAPI architecture with separation of concerns |
| **Implementation Effectiveness** | Working pipeline: Jira → LLM → Playwright → Jira |
| **Team Fit & Collaboration** | Transparent updates, clear documentation, structured tickets |
| **Bonus Effort** | Includes architecture diagram, extensible design, and demo readiness |

---

## 🎥 Demo Preparation

Your final presentation should highlight:
- **Architecture overview** (use diagram above)  
- **Live or recorded demo** of a validation run  
- **Challenges & learnings**  
- **Next-step recommendations**  

Include a short Loom or video link here if possible:
> 🎬 *Demo Video:* [Insert Loom or YouTube link here]*

---

## 👤 Author

**Emmanuel Ayodele**  
Engineering Trial — *“See If We Can Work Together”*  
Curacel, 2025  

📧 [ayodele.e@curacel.ai]  
🌐 [LinkedIn](https://linkedin.com/in/emmanuel-t-ayodele) | [GitHub](https://github.com/emmahmusk)
