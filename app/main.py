from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.database import engine, Base
from app.routers import students, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Scalable Student Management System with LangGraph Gemini Assistant & SQLite.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router)
app.include_router(chat.router)

# Mount static files folder
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the visual dashboard on the root URL
@app.get("/", tags=["Dashboard"])
def get_dashboard():
    return FileResponse("static/index.html")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "database": "sqlite", "ai_agent": "langgraph-gemini"}