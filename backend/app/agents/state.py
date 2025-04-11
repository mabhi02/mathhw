import logging
from typing import Dict, Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import Depends

from backend.app.db.session import get_db
from backend.app.agents.base import AbstractAgent, AgentRequest
from backend.app.models.agent_state import AgentState
from backend.app.crud.agent_state import agent_state as agent_state_crud

# Setup logger
logger = logging.getLogger("app.agents.state")

class StatefulAgent(AbstractAgent):
    """
    Agent mixin that adds database state persistence
    
    This class extends AbstractAgent with methods for state management
    that store agent state in the database rather than memory.
    """
    
    async def load_state(self, request: AgentRequest, db: Optional[Session] = None) -> Dict[str, Any]:
        """
        Load agent state from database
        
        Args:
            request: Agent request with context
            db: Optional database session, obtained from dependency if not provided
            
        Returns:
            Agent state data
        """
        # Close DB session when done if we created it
        close_db = False
        
        try:
            # Get database session if not provided
            if db is None:
                db = next(get_db())
                close_db = True
            
            # Get state ID from request or use agent ID
            state_id = request.state_id or self.agent_id
            
            # Get state from database
            db_state = agent_state_crud.get_by_agent_id(db, state_id) 
            
            if not db_state:
                logger.info(f"No existing state found for agent {self.agent_id}, initializing empty state")
                return {}
            
            logger.info(f"Loaded state for agent {self.agent_id} (version {db_state.version})")
            return db_state.state_data
            
        except Exception as e:
            logger.error(f"Error loading agent state: {str(e)}")
            return {}
            
        finally:
            # Close DB session if we created it
            if close_db and db:
                db.close()
    
    async def save_state(
        self, 
        request: AgentRequest, 
        state: Dict[str, Any],
        db: Optional[Session] = None
    ) -> str:
        """
        Save agent state to database
        
        Args:
            request: Agent request with context
            state: State data to save
            db: Optional database session, obtained from dependency if not provided
            
        Returns:
            State ID
        """
        # Close DB session when done if we created it
        close_db = False
        
        try:
            # Get database session if not provided
            if db is None:
                db = next(get_db())
                close_db = True
            
            # Get state ID from request or use agent ID
            state_id = request.state_id or self.agent_id
            pipeline_id = getattr(request.context, 'trace_id', None)
            
            # Get existing state or create new
            db_state = agent_state_crud.get_by_agent_id(db, state_id)
            
            if db_state:
                # Update existing state
                agent_state_crud.update_state_data(
                    db=db,
                    db_obj=db_state,
                    state_data=state,
                    create_checkpoint=True,
                    checkpoint_reason=f"Update from request {request.context.request_id}"
                )
                logger.info(f"Updated state for agent {self.agent_id} (version {db_state.version})")
                return db_state.id
            else:
                # Create new state
                from backend.app.schemas.agent_state import AgentStateCreate
                
                new_state = AgentStateCreate(
                    agent_id=self.agent_id,
                    agent_type=self.__class__.__name__,
                    pipeline_id=pipeline_id,
                    state_data=state
                )
                
                db_state = agent_state_crud.create(db=db, obj_in=new_state)
                logger.info(f"Created new state for agent {self.agent_id} (id {db_state.id})")
                return db_state.id
                
        except Exception as e:
            logger.error(f"Error saving agent state: {str(e)}")
            return self.agent_id
            
        finally:
            # Close DB session if we created it
            if close_db and db:
                db.close()


class DatabaseStateMixin:
    """
    Mixin to add database state capabilities to any agent
    
    This mixin is simpler than the StatefulAgent and can be added to any
    existing agent class.
    """
    async def load_state(self, request: AgentRequest) -> Dict[str, Any]:
        """Load state from database"""
        db = next(get_db())
        try:
            state_id = request.state_id or self.agent_id
            db_state = agent_state_crud.get_by_agent_id(db, state_id)
            
            if not db_state:
                return {}
                
            return db_state.state_data
        finally:
            db.close()
            
    async def save_state(self, request: AgentRequest, state: Dict[str, Any]) -> str:
        """Save state to database"""
        db = next(get_db())
        try:
            state_id = request.state_id or self.agent_id
            pipeline_id = getattr(request.context, 'trace_id', None)
            
            db_state = agent_state_crud.get_by_agent_id(db, state_id)
            
            if db_state:
                agent_state_crud.update_state_data(
                    db=db,
                    db_obj=db_state,
                    state_data=state,
                    create_checkpoint=True
                )
                return db_state.id
            else:
                from backend.app.schemas.agent_state import AgentStateCreate
                
                new_state = AgentStateCreate(
                    agent_id=self.agent_id,
                    agent_type=self.__class__.__name__,
                    pipeline_id=pipeline_id,
                    state_data=state
                )
                
                db_state = agent_state_crud.create(db=db, obj_in=new_state)
                return db_state.id
        finally:
            db.close() 