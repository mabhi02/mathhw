from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging

from backend.app.agents import AgentFactory, execute_agent_pipeline
from backend.app.agents.pipeline import PipelineStep
from backend.app.db.session import get_db
from sqlalchemy.orm import Session

# Setup logger
logger = logging.getLogger("app.routes.pipeline")

# Create router
router = APIRouter()

# Request/response models
class PipelineStepConfig(BaseModel):
    """Configuration for a pipeline step"""
    agent_type: str
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)

class PipelineExecuteRequest(BaseModel):
    """Request to execute a pipeline"""
    steps: List[PipelineStepConfig]
    initial_prompt: str
    system_prompt: Optional[str] = None

class PipelineStepResult(BaseModel):
    """Result of a pipeline step"""
    step: str
    agent_id: str
    agent_name: str
    success: bool
    elapsed_time: float

class PipelineExecuteResponse(BaseModel):
    """Response from pipeline execution"""
    pipeline_id: str
    elapsed_time: float
    success: bool
    error: Optional[str] = None
    steps: List[PipelineStepResult]
    final_output: Optional[str] = None
    final_data: Optional[Dict[str, Any]] = None

# Routes
@router.get("/agent-types", response_model=List[str])
async def get_available_agent_types():
    """Get list of available agent types for pipelines"""
    return AgentFactory.list_agent_types()

@router.post("/execute", response_model=PipelineExecuteResponse)
async def execute_pipeline(
    request: PipelineExecuteRequest,
    db: Session = Depends(get_db)
):
    """
    Execute an agent pipeline
    
    Executes a sequence of agents where the output of each agent is passed as
    input to the next agent.
    """
    try:
        # Convert request to step configs
        step_configs = [step.dict() for step in request.steps]
        
        # Execute pipeline
        result = await execute_agent_pipeline(
            step_configs=step_configs,
            initial_prompt=request.initial_prompt,
            system_prompt=request.system_prompt
        )
        
        # Return result
        return result
    except Exception as e:
        logger.error(f"Error executing pipeline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing pipeline: {str(e)}"
        ) 