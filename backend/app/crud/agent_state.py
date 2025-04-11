from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.crud.base import CRUDBase
from backend.app.models.agent_state import AgentState, AgentStateCheckpoint
from backend.app.schemas.agent_state import AgentStateCreate, AgentStateUpdate

class CRUDAgentState(CRUDBase[AgentState, AgentStateCreate, AgentStateUpdate]):
    """
    CRUD operations for agent state
    """
    def get_by_agent_id(self, db: Session, agent_id: str) -> Optional[AgentState]:
        """
        Get active state by agent_id
        
        Args:
            db: Database session
            agent_id: Agent ID
            
        Returns:
            Optional agent state
        """
        return db.query(self.model).filter(
            self.model.agent_id == agent_id,
            self.model.is_active == True
        ).first()
    
    def get_by_pipeline(self, db: Session, pipeline_id: str) -> List[AgentState]:
        """
        Get all agent states for a pipeline
        
        Args:
            db: Database session
            pipeline_id: Pipeline ID
            
        Returns:
            List of agent states
        """
        return db.query(self.model).filter(
            self.model.pipeline_id == pipeline_id,
            self.model.is_active == True
        ).all()
        
    def update_state_data(
        self, 
        db: Session, 
        db_obj: AgentState,
        state_data: Dict[str, Any],
        create_checkpoint: bool = True,
        checkpoint_reason: Optional[str] = None
    ) -> AgentState:
        """
        Update state data with checkpointing
        
        Args:
            db: Database session
            db_obj: Agent state object
            state_data: New state data to set
            create_checkpoint: Whether to create a checkpoint
            checkpoint_reason: Optional reason for the checkpoint
            
        Returns:
            Updated agent state
        """
        # Create checkpoint if requested
        if create_checkpoint:
            checkpoint = db_obj.create_checkpoint(reason=checkpoint_reason)
            db.add(checkpoint)
        
        # Update state data
        db_obj.state_data = state_data
        db_obj.last_executed = datetime.utcnow().isoformat()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def rollback_to_checkpoint(
        self, 
        db: Session,
        db_obj: AgentState,
        checkpoint_id: str
    ) -> AgentState:
        """
        Rollback state to a specific checkpoint
        
        Args:
            db: Database session
            db_obj: Agent state object
            checkpoint_id: ID of checkpoint to roll back to
            
        Returns:
            Updated agent state
        """
        # Find checkpoint
        checkpoint = db.query(AgentStateCheckpoint).filter(
            AgentStateCheckpoint.id == checkpoint_id,
            AgentStateCheckpoint.agent_state_id == db_obj.id
        ).first()
        
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
            
        # Update state with checkpoint data
        db_obj.state_data = checkpoint.state_data
        db_obj.version = checkpoint.version
        
        # Add checkpoint for rollback
        rollback_checkpoint = db_obj.create_checkpoint(
            reason=f"Rollback to checkpoint {checkpoint_id}"
        )
        db.add(rollback_checkpoint)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
        
    def list_checkpoints(
        self,
        db: Session,
        agent_state_id: str
    ) -> List[AgentStateCheckpoint]:
        """
        List all checkpoints for an agent state
        
        Args:
            db: Database session
            agent_state_id: Agent state ID
            
        Returns:
            List of checkpoints
        """
        return db.query(AgentStateCheckpoint).filter(
            AgentStateCheckpoint.agent_state_id == agent_state_id
        ).order_by(AgentStateCheckpoint.created_at.desc()).all()
        
        
# Create CRUD instance
agent_state = CRUDAgentState(AgentState) 