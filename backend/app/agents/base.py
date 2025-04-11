from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union, Protocol
from pydantic import BaseModel, Field
import uuid
import logging
import asyncio
from datetime import datetime

from backend.app.llm import LLMProvider, get_llm_provider

# Setup logger
logger = logging.getLogger("app.agents")

class AgentContext(BaseModel):
    """Context information for agent execution"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: Optional[str] = None
    parent_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"arbitrary_types_allowed": True}

class ToolDefinition(BaseModel):
    """Definition of a tool that an agent can use"""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    required_parameters: List[str] = Field(default_factory=list)
    
    model_config = {"arbitrary_types_allowed": True}

class AgentRequest(BaseModel):
    """
    Request to an agent
    
    Contains the prompt, any system prompt override, context information,
    and additional parameters.
    """
    prompt: str
    system_prompt: Optional[str] = None
    context: AgentContext = Field(default_factory=AgentContext)
    params: Dict[str, Any] = Field(default_factory=dict)
    
    # Optional state management
    load_state: bool = False
    save_state: bool = True
    state_id: Optional[str] = None
    
    model_config = {"arbitrary_types_allowed": True}
    
    def with_context(self) -> "AgentRequest":
        """
        Ensure the request has a valid context
        
        Returns:
            Self, for method chaining
        """
        if not self.context:
            self.context = AgentContext()
        return self

class AgentResponse(BaseModel):
    """
    Response from an agent
    
    Contains the text response, metadata about the execution,
    and status information.
    """
    text: str
    request_id: str
    agent_id: str
    agent_name: str
    elapsed_time: float
    output_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
    state_id: Optional[str] = None
    
    model_config = {"arbitrary_types_allowed": True}

class AbstractAgent(ABC):
    """
    Abstract base class for agents
    
    All agents must implement the execute method which processes
    a request and returns a response.
    """
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        instructions: str,
        llm_provider: Optional[LLMProvider] = None,
        tools: Optional[List[ToolDefinition]] = None,
        state_enabled: bool = True,
        **kwargs
    ):
        """
        Initialize agent
        
        Args:
            agent_id: Unique identifier for this agent
            name: Human-readable name
            description: Description of the agent's purpose
            instructions: Base instructions for the agent
            llm_provider: Optional LLM provider, defaults to global provider
            tools: Optional list of tools the agent can use
            state_enabled: Whether state persistence is enabled for this agent
            **kwargs: Additional configuration parameters
        """
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.instructions = instructions
        self.llm_provider = llm_provider or get_llm_provider()
        self.tools = tools or []
        self.state_enabled = state_enabled
        self.config = kwargs
        self._state = {}
        
        logger.info(f"Initialized agent: {self.name} ({self.agent_id})")
    
    def format_system_prompt(self, request: AgentRequest) -> str:
        """
        Format system prompt with instructions
        
        Args:
            request: Agent request with optional system prompt
            
        Returns:
            Formatted system prompt
        """
        if request.system_prompt:
            return f"{self.instructions}\n\n{request.system_prompt}"
        return self.instructions
    
    async def load_state(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Load agent state
        
        This method can be overridden by subclasses to load state from
        a persistent store rather than memory.
        
        Args:
            request: Agent request with context
            
        Returns:
            Agent state
        """
        # Default implementation uses in-memory state
        # Subclasses should override to load from database if needed
        return self._state
    
    async def save_state(self, request: AgentRequest, state: Dict[str, Any]) -> str:
        """
        Save agent state
        
        This method can be overridden by subclasses to save state to
        a persistent store rather than memory.
        
        Args:
            request: Agent request with context
            state: State to save
            
        Returns:
            State ID
        """
        # Default implementation saves to in-memory state
        # Subclasses should override to save to database if needed
        self._state = state
        return self.agent_id
    
    async def execute_with_tools(self, request: AgentRequest) -> AgentResponse:
        """
        Execute the agent using tools
        
        This method processes a request and allows the agent to use tools
        to generate a response.
        
        Args:
            request: Request to process
            
        Returns:
            Agent response
        """
        try:
            start_time = datetime.utcnow()
            
            # Prepare prompt
            system_prompt = self.format_system_prompt(request)
            
            # Execute with LLM provider
            result = await self.llm_provider.invoke_with_tools(
                system_prompt=system_prompt,
                user_prompt=request.prompt,
                tools=self.tools,
                model=self.config.get("model")
            )
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Executed agent {self.name} with tools in {elapsed:.2f}s")
            
            response = AgentResponse(
                text=result.get("text", ""),
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                output_data={"tool_calls": result.get("tool_calls", [])},
                metadata={
                    "model": result.get("model", "unknown"),
                    "tools_used": [t.name for t in self.tools]
                },
                success=result.get("success", False)
            )
            
            if not result.get("success"):
                response.error = result.get("error", "Unknown error")
                
            return response
            
        except Exception as e:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error executing agent {self.name}: {str(e)}")
            
            return AgentResponse(
                text=f"Error: {str(e)}",
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                error=str(e),
                success=False
            )
    
    @abstractmethod
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute the agent with the given request
        
        Args:
            request: Request to process
            
        Returns:
            Agent response
        """
        pass
    
    async def execute_with_state(self, request: AgentRequest) -> AgentResponse:
        """
        Execute the agent with state management
        
        This method wraps the execute method with state loading and saving.
        
        Args:
            request: Request to process
            
        Returns:
            Agent response with state information
        """
        # Skip state if not enabled
        if not self.state_enabled:
            return await self.execute(request)
        
        # Load state if requested
        if request.load_state:
            try:
                state = await self.load_state(request)
                logger.info(f"Loaded state for agent {self.name} ({self.agent_id})")
                self._state = state
            except Exception as e:
                logger.error(f"Error loading state for agent {self.name}: {str(e)}")
                return AgentResponse(
                    text=f"Error loading agent state: {str(e)}",
                    request_id=request.context.request_id,
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    elapsed_time=0.0,
                    error=str(e),
                    success=False
                )
        
        # Execute the agent
        response = await self.execute(request)
        
        # Save state if requested and execution was successful
        if request.save_state and response.success:
            try:
                state_id = await self.save_state(request, self._state)
                response.state_id = state_id
                logger.info(f"Saved state for agent {self.name} ({self.agent_id})")
            except Exception as e:
                logger.error(f"Error saving state for agent {self.name}: {str(e)}")
                # Don't fail the response if state saving fails
        
        return response

class LLMAgent(AbstractAgent):
    """
    Basic LLM-based agent implementation
    
    This agent simply forwards the request to the LLM provider.
    """
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute the agent with the given request
        
        Args:
            request: Request to process
            
        Returns:
            Agent response
        """
        start_time = datetime.utcnow()
        request = request.with_context()
        
        try:
            system_prompt = self.format_system_prompt(request)
            
            result = await self.llm_provider.generate(
                prompt=request.prompt,
                system_prompt=system_prompt,
                **request.params
            )
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            response = AgentResponse(
                text=result.get("text", ""),
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                metadata={"model": result.get("model", "unknown")},
                success=result.get("success", False)
            )
            
            if not result.get("success"):
                response.error = result.get("error", "Unknown error")
                
            return response
            
        except Exception as e:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error executing agent {self.name}: {str(e)}")
            
            return AgentResponse(
                text=f"Error: {str(e)}",
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                error=str(e),
                success=False
            ) 