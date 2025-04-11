from sqlalchemy import Column, String, JSON, ForeignKey, Boolean, Text, Integer
from sqlalchemy.orm import relationship
import uuid

from backend.app.db.base import TimestampedBase

class AgentState(TimestampedBase):
    """
    Model for storing agent state
    
    This model persists the state of agents between executions, allowing
    for stateful processing and the ability to resume or rollback operations.
    """
    __tablename__ = "agent_states"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(255), nullable=False, index=True)
    agent_type = Column(String(255), nullable=False, index=True)
    
    # Current state data
    state_data = Column(JSON, nullable=False, default=dict)
    
    # Pipeline information
    pipeline_id = Column(String(255), nullable=True, index=True)
    step_name = Column(String(255), nullable=True)
    
    # Status information
    is_active = Column(Boolean, default=True, nullable=False)
    locked = Column(Boolean, default=False, nullable=False)
    last_executed = Column(String(255), nullable=True)  # ISO timestamp
    
    # Metadata and version tracking
    version = Column(Integer, default=1, nullable=False)
    checkpoints = relationship("AgentStateCheckpoint", back_populates="agent_state", 
                               cascade="all, delete-orphan", order_by="AgentStateCheckpoint.created_at")
    
    def __repr__(self):
        return f"<AgentState id={self.id} agent_id={self.agent_id} version={self.version}>"
    
    def create_checkpoint(self, reason: str = None) -> "AgentStateCheckpoint":
        """
        Create a checkpoint of the current state
        
        Args:
            reason: Optional reason for creating checkpoint
            
        Returns:
            New checkpoint
        """
        checkpoint = AgentStateCheckpoint(
            agent_state_id=self.id,
            state_data=self.state_data,
            version=self.version,
            reason=reason
        )
        self.version += 1
        return checkpoint


class AgentStateCheckpoint(TimestampedBase):
    """
    Model for storing checkpoints of agent state
    
    Checkpoints allow rolling back to previous states in case of errors
    or when implementing undo functionality.
    """
    __tablename__ = "agent_state_checkpoints"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_state_id = Column(String(36), ForeignKey("agent_states.id"), nullable=False)
    state_data = Column(JSON, nullable=False)
    version = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)
    
    # Relationship
    agent_state = relationship("AgentState", back_populates="checkpoints")
    
    def __repr__(self):
        return f"<AgentStateCheckpoint id={self.id} version={self.version}>" 