from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.crud.agent_state import agent_state as agent_state_crud
from backend.app.schemas.agent_state import (
    AgentState, AgentStateList, AgentStateUpdate,
    AgentStateCheckpoint, AgentStateCheckpointList
)

# Setup logger
logger = logging.getLogger("app.routes.agent_state")

# Create router
router = APIRouter()

# Routes
@router.get("/agents/{agent_id}/state", response_model=AgentState)
async def get_agent_state(agent_id: str, db: Session = Depends(get_db)):
    """
    Get the current state for an agent
    
    Args:
        agent_id: Agent ID
        
    Returns:
        Agent state
    """
    state = agent_state_crud.get_by_agent_id(db, agent_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State not found for agent {agent_id}"
        )
    return state


@router.get("/states/{state_id}", response_model=AgentState)
async def get_state_by_id(state_id: str, db: Session = Depends(get_db)):
    """
    Get state by ID
    
    Args:
        state_id: State ID
        
    Returns:
        Agent state
    """
    state = agent_state_crud.get(db, state_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State not found: {state_id}"
        )
    return state


@router.get("/pipelines/{pipeline_id}/states", response_model=AgentStateList)
async def get_pipeline_states(pipeline_id: str, db: Session = Depends(get_db)):
    """
    Get all states for a pipeline
    
    Args:
        pipeline_id: Pipeline ID
        
    Returns:
        List of agent states
    """
    states = agent_state_crud.get_by_pipeline(db, pipeline_id)
    return {
        "items": states,
        "total": len(states)
    }


@router.get("/states/{state_id}/checkpoints", response_model=AgentStateCheckpointList)
async def get_state_checkpoints(state_id: str, db: Session = Depends(get_db)):
    """
    Get checkpoints for a state
    
    Args:
        state_id: State ID
        
    Returns:
        List of checkpoints
    """
    state = agent_state_crud.get(db, state_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State not found: {state_id}"
        )
    
    checkpoints = agent_state_crud.list_checkpoints(db, state_id)
    return {
        "items": checkpoints,
        "total": len(checkpoints)
    }


@router.post("/states/{state_id}/rollback/{checkpoint_id}", response_model=AgentState)
async def rollback_to_checkpoint(state_id: str, checkpoint_id: str, db: Session = Depends(get_db)):
    """
    Rollback a state to a checkpoint
    
    Args:
        state_id: State ID
        checkpoint_id: Checkpoint ID to rollback to
        
    Returns:
        Updated agent state
    """
    state = agent_state_crud.get(db, state_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State not found: {state_id}"
        )
    
    try:
        updated_state = agent_state_crud.rollback_to_checkpoint(db, state, checkpoint_id)
        return updated_state
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/states/{state_id}", response_model=AgentState)
async def update_state(
    state_id: str, 
    update_data: AgentStateUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an agent state
    
    Args:
        state_id: State ID
        update_data: Data to update
        
    Returns:
        Updated agent state
    """
    state = agent_state_crud.get(db, state_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State not found: {state_id}"
        )
    
    updated_state = agent_state_crud.update(db, db_obj=state, obj_in=update_data)
    return updated_state 