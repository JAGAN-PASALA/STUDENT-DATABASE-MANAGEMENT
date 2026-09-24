# Student Database Management System with Gemini AI Assistant

A full-stack student management portal built with **FastAPI**, **SQLite**, and **Google Gemini AI** via the modern `google-genai` SDK.

The system features native CRUD operations for student records combined with an autonomous AI chat assistant capable of real-time SQLite schema inspection, SQL translation, and execution with automated model failover.

---

## Features

- **Full Student CRUD Directory**: Create, read, edit, delete, and view profile records with client-side safe back-navigation and data validation.
- **Natural Language Database Querying**: Translates user questions into read-only SQLite `SELECT` queries without vector databases or embedding indexing.
- **Dynamic Failover Architecture**: Automatic failover chain (`gemini-2.5-flash-lite`, `gemini-2.5-flash`, `gemini-2.0-flash`, etc.) mitigating `429 RESOURCE_EXHAUSTED` quotas and `503 UNAVAILABLE` cloud spikes.
- **Safe Interactive UI**: Integrated dashboard with smart chat auto-scrolling that detects manual reading positions to prevent view jumping.
- **Interactive API Docs**: Built-in Swagger UI and OpenAPI documentation at `/docs`.

---

## Tech Stack

- **Backend**: FastAPI, Uvicorn, SQLAlchemy, Pydantic v2
- **Database**: SQLite (Zero configuration, auto-generated on startup)
- **AI Agent**: Google GenAI SDK (`google-genai`) with Automatic Function Calling (AFC)
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, Tailwind CSS, FontAwesome
- **Containerization**: Docker & Docker Compose

---

## Quickstart (Local Python)

### 1. Clone Repository
```bash
git clone [https://github.com/](https://github.com/)<your-username>/student-database-management.git
cd student-database-management
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file from the provided template:
```bash
cp .env.example .env
```
Open `.env` and set your key from [Google AI Studio](https://aistudio.google.com/app/apikey):
```ini
GEMINI_API_KEY=AIzaSyYourActualKeyHere
```

### 5. Run Server
```bash
python -m uvicorn app.main:app --reload
```
Open your browser at `http://127.0.0.1:8000`.

---

## Run with Docker

Run the entire system in an isolated container without local Python dependencies:

```bash
# 1. Ensure .env has your GEMINI_API_KEY
# 2. Build and launch container
docker compose up --build -d
```
Access the application at `http://localhost:8000`.

To stop the container:
```bash
docker compose down
```

---

## API Documentation

FastAPI auto-generates interactive API documentation:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

---

## Project Structure

```text
├── app/
│   ├── chatbot/
│   │   ├── graph.py         # Gemini client & tool execution failover loop
│   │   └── tools.py         # SQLite schema & read-only execution tools
│   ├── routers/
│   │   ├── chat.py          # AI query API router
│   │   └── students.py      # Student CRUD operations router
│   ├── config.py            # Environment settings (Pydantic Settings)
│   ├── crud.py              # SQLAlchemy database queries
│   ├── database.py          # Engine & session setup
│   ├── main.py              # FastAPI app definition & lifespan handlers
│   ├── models.py            # SQLAlchemy ORM student model
│   └── schemas.py           # Pydantic request/response validation schemas
├── static/
│   └── index.html           # Full Single-Page Application (SPA) dashboard
├── .env.example             # Template environment configuration
├── .gitignore               # Excludes secrets, venv, and local database files
├── Dockerfile               # Production container image
├── docker-compose.yml       # Service orchestration definition
├── requirements.txt         # Pinned python dependencies
└── README.md                # Project documentation
```