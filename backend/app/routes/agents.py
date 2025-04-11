from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging

from backend.app.agents import AgentFactory, AgentRequest, AgentResponse
from backend.app.db.session import get_db
from sqlalchemy.orm import Session

# Setup logger
logger = logging.getLogger("app.routes.agents")

# Create router
router = APIRouter()

# Request/response models
class AgentRequestModel(BaseModel):
    """Agent request API model"""
    prompt: str
    system_prompt: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)

class AgentResponseModel(BaseModel):
    """Agent response API model"""
    text: str
    agent_id: str
    agent_name: str
    elapsed_time: float = 0.0
    output_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    success: bool = True

# Routes
@router.get("/types", response_model=List[str])
async def get_agent_types():
    """Get list of available agent types"""
    return AgentFactory.list_agent_types()

@router.post("/{agent_type}/execute", response_model=AgentResponseModel)
async def execute_agent(
    agent_type: str,
    request: AgentRequestModel,
    db: Session = Depends(get_db)
):
    """
    Execute an agent with the given request
    
    Creates an agent of the specified type and executes it with the given request.
    """
    try:
        # Create agent instance
        agent = AgentFactory.create_agent(agent_type)
        
        # Create agent request
        agent_request = AgentRequest(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            params=request.params
        )
        
        # Execute agent
        response = await agent.execute(agent_request)
        
        # Convert to API response
        return AgentResponseModel(
            text=response.text,
            agent_id=response.agent_id,
            agent_name=response.agent_name,
            elapsed_time=response.elapsed_time,
            output_data=response.output_data,
            metadata=response.metadata,
            error=response.error,
            success=response.success
        )
    except Exception as e:
        logger.error(f"Error executing agent {agent_type}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing agent: {str(e)}"
        ) 