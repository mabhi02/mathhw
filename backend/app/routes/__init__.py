from fastapi import APIRouter

from backend.app.routes import (
    questions,
    outlines,
    templates,
    agent_state,
    pipeline,
    agents,
    feedback,
    comparisons,
)

# Create main API router
api_router = APIRouter()

# Define tag descriptions for Swagger UI
tag_descriptions = [
    {
        "name": "questions",
        "description": "Operations with questions and question generation"
    },
    {
        "name": "outlines",
        "description": "Operations with outlines that structure question generation"
    },
    {
        "name": "templates",
        "description": "Operations with question templates"
    },
    {
        "name": "agent-state",
        "description": "Operations for managing agent state"
    },
    {
        "name": "pipeline",
        "description": "Operations for agent pipeline execution"
    },
    {
        "name": "agents",
        "description": "Operations for agent management"
    },
    {
        "name": "feedback",
        "description": "Operations for user feedback on generated questions"
    },
    {
        "name": "comparisons",
        "description": "Operations for comparing different question generation strategies"
    },
    {
        "name": "enhanced",
        "description": "Enhanced endpoints using OpenAI Agents SDK for sophisticated multi-agent workflows"
    },
    {
        "name": "Health",
        "description": "Health check endpoints"
    },
    {
        "name": "Documentation",
        "description": "Documentation endpoints"
    }
]

# Include sub-routers
api_router.include_router(questions.router, prefix="/questions")
api_router.include_router(outlines.router, prefix="/outlines")
api_router.include_router(templates.router, prefix="/templates")
api_router.include_router(agent_state.router, prefix="/agent-state")
api_router.include_router(pipeline.router, prefix="/pipeline")
api_router.include_router(agents.router, prefix="/agents")
api_router.include_router(feedback.router, prefix="/feedback")
api_router.include_router(comparisons.router, prefix="/comparisons")
