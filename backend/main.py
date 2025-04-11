# backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import uvicorn
import logging
import os
from typing import Dict, List

# Import our application modules
from backend.app.core.logging import configure_logging
from backend.app.config import get_settings, Settings
from backend.app.agents.factory import AgentFactory
from backend.app.routes import api_router, tag_descriptions

# Initialize settings
settings = get_settings()

# Configure structured logging
configure_logging(
    app_name=settings.APP_NAME,
    log_level="DEBUG" if settings.DEBUG else "INFO",
    json_logs=False  # Set to True in production
)

# Get logger
logger = logging.getLogger("app.main")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Agent-Based Text System for generating questions from outlines",
    version=settings.API_VERSION,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    contact={
        "name": "ABTS Team",
        "url": "https://github.com/your-org/abts-unified-generator",
    },
    license_info={
        "name": "MIT",
    },
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # Hide schemas by default
        "deepLinking": True,  # Allow deeplinking tags, operations
        "displayRequestDuration": True,  # Show request duration
        "syntaxHighlight.theme": "monokai",  # Syntax highlighting theme
        "filter": True,  # Enable filtering operations
    },
    openapi_tags=tag_descriptions,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend/app/static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info(f"Static files directory mounted at {static_dir}")
else:
    logger.warning(f"Static files directory not found at {static_dir}")

# Include API routes
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "online", 
        "service": settings.APP_NAME,
        "version": settings.API_VERSION
    }

@app.get("/docs", tags=["Documentation"])
async def docs_redirect():
    """Redirect to API documentation"""
    return RedirectResponse(url=f"{settings.API_PREFIX}/docs")

@app.get("/api-docs", tags=["Documentation"])
async def custom_docs():
    """Redirect to custom API documentation"""
    return RedirectResponse(url="/static/docs.html")

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    logger.info(f"Starting {settings.APP_NAME} service")
    
    # Start configuration hot-reloading
    settings.start_hot_reload()
    logger.info("Configuration hot-reloading enabled")
    
    # Initialize agent factory on startup
    AgentFactory.initialize()
    logger.info("Agent factory initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"Shutting down {settings.APP_NAME} service")
    
    # Stop configuration hot-reloading
    settings.stop_hot_reload()
    logger.info("Configuration hot-reloading stopped")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)