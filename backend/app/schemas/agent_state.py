from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# Shared properties
class AgentStateBase(BaseModel):
    """Base schema for agent state"""
    agent_id: str = Field(description="ID of the agent")
    agent_type: str = Field(description="Type of the agent")
    pipeline_id: Optional[str] = Field(None, description="ID of the pipeline this agent is part of")
    step_name: Optional[str] = Field(None, description="Name of the pipeline step")
    is_active: bool = Field(True, description="Whether this state is active")
    
    
# Properties to receive on state creation
class AgentStateCreate(AgentStateBase):
    """Schema for creating agent state"""
    state_data: Dict[str, Any] = Field(default_factory=dict, description="State data")
    

# Properties to receive on state update
class AgentStateUpdate(BaseModel):
    """Schema for updating agent state"""
    state_data: Optional[Dict[str, Any]] = Field(None, description="State data to update")
    pipeline_id: Optional[str] = Field(None, description="Pipeline ID")
    step_name: Optional[str] = Field(None, description="Step name")
    is_active: Optional[bool] = Field(None, description="Active status")
    locked: Optional[bool] = Field(None, description="Locked status")


# Properties shared by models stored in DB
class AgentStateInDBBase(AgentStateBase):
    """Base schema for agent state in database"""
    id: str
    state_data: Dict[str, Any]
    version: int
    locked: bool
    last_executed: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


# Properties to return to client
class AgentState(AgentStateInDBBase):
    """Schema for agent state responses"""
    pass


# Checkpoint schemas
class AgentStateCheckpointBase(BaseModel):
    """Base schema for agent state checkpoint"""
    agent_state_id: str = Field(description="ID of the agent state")
    version: int = Field(description="Version number")
    reason: Optional[str] = Field(None, description="Reason for creating this checkpoint")


# Properties to receive on checkpoint creation
class AgentStateCheckpointCreate(AgentStateCheckpointBase):
    """Schema for creating agent state checkpoint"""
    state_data: Dict[str, Any] = Field(description="State data at checkpoint")


# Properties to return to client
class AgentStateCheckpoint(AgentStateCheckpointBase):
    """Schema for agent state checkpoint responses"""
    id: str
    state_data: Dict[str, Any]
    created_at: datetime
    
    model_config = {"from_attributes": True}


# List schemas
class AgentStateList(BaseModel):
    """Schema for list of agent states"""
    items: List[AgentState]
    total: int
    
    
class AgentStateCheckpointList(BaseModel):
    """Schema for list of agent state checkpoints"""
    items: List[AgentStateCheckpoint]
    total: int 