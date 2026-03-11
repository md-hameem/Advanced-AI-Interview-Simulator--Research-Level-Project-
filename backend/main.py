"""
Advanced AI Interview Simulator - FastAPI Application
Main entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db
from routers.interview import router as interview_router
from routers.speech import router as speech_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    logger.info("🚀 Initializing AI Interview Simulator...")
    init_db()
    logger.info("✅ Database initialized")
    logger.info(f"📡 LLM Model: {settings.LLM_MODEL}")
    logger.info(f"🔑 Gemini API Key: {'configured' if settings.GEMINI_API_KEY else 'NOT SET'}")
    yield
    logger.info("👋 Shutting down AI Interview Simulator")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered technical interview simulator with adaptive questioning, "
                "rubric-based evaluation, and comprehensive candidate assessment.",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(interview_router)
app.include_router(speech_router)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
