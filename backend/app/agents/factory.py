import logging
from typing import Dict, Any, Type, List, Optional
import uuid

from backend.app.config import get_settings
from backend.app.agents.base import AbstractAgent, LLMAgent, ToolDefinition
from backend.app.llm import get_llm_provider

# Setup logger
logger = logging.getLogger("app.agents.factory")

class AgentFactory:
    """
    Factory class for creating agent instances
    
    The factory loads agent configurations from agent_definitions.yml
    and handles instantiation of agent classes based on their type.
    """
    _registry: Dict[str, Type[AbstractAgent]] = {}
    _instances: Dict[str, AbstractAgent] = {}
    _agent_configs: Dict[str, Dict[str, Any]] = {}
    _tool_definitions: Dict[str, Any] = {}
    _initialized = False
    
    @classmethod
    def get_instance(cls):
        """
        Get the singleton instance of the factory
        
        Returns:
            AgentFactory class with initialized state
        """
        if not cls._initialized:
            cls.initialize()
        return cls
    
    @classmethod
    def register(cls, agent_type: str, agent_cls: Type[AbstractAgent]):
        """
        Register an agent class with the factory
        
        Args:
            agent_type: Type identifier for the agent
            agent_cls: Agent class to register
        """
        cls._registry[agent_type] = agent_cls
        logger.info(f"Registered agent type: {agent_type}")
    
    @classmethod
    def initialize(cls):
        """
        Initialize the factory with configuration from agent_definitions.yml
        """
        if cls._initialized:
            logger.info("AgentFactory already initialized")
            return
        
        settings = get_settings()
        
        try:
            # Load agent configurations from YAML
            agent_defs = settings.get_agent_definitions()
            
            # Store agent configurations
            cls._agent_configs = agent_defs.get("agents", {})
            
            # Store tool definitions
            cls._tool_definitions = agent_defs.get("tools", {})
            
            # Register base agent types
            cls.register("llm", LLMAgent)
            
            cls._initialized = True
            logger.info(f"Initialized AgentFactory with {len(cls._agent_configs)} agent types")
            
        except Exception as e:
            logger.error(f"Error initializing AgentFactory: {e}")
            raise
    
    @classmethod
    def get_tool_definition(cls, tool_name: str) -> Optional[ToolDefinition]:
        """
        Get a tool definition by name
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool definition or None if not found
        """
        if not cls._initialized:
            cls.initialize()
            
        if tool_name not in cls._tool_definitions:
            return None
            
        tool_config = cls._tool_definitions[tool_name]
        
        parameters = []
        for param in tool_config.get("parameters", []):
            parameters.append({
                "name": param.get("name", ""),
                "description": param.get("description", ""),
                "type": param.get("type", "string"),
                "required": param.get("required", True)
            })
        
        return ToolDefinition(
            name=tool_name,
            description=tool_config.get("description", ""),
            parameters=parameters,
            returns=tool_config.get("returns", None)
        )
    
    @classmethod
    def create_agent(cls, agent_type: str, agent_id: Optional[str] = None) -> AbstractAgent:
        """
        Create an agent instance by type
        
        Args:
            agent_type: Type of agent to create
            agent_id: Optional agent ID, generated if not provided
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If agent type is not registered or configured
        """
        if not cls._initialized:
            cls.initialize()
        
        if agent_type not in cls._agent_configs:
            raise ValueError(f"Agent type not configured: {agent_type}")
        
        config = cls._agent_configs[agent_type]
        
        # Use provided ID or generate one
        agent_id = agent_id or f"{agent_type}-{str(uuid.uuid4())[:8]}"
        
        # Get agent class (default to LLMAgent)
        agent_cls = cls._registry.get(agent_type, LLMAgent)
        
        # Get tools if specified
        tools = []
        if "tools" in config and config["tools"] is not None:
            for tool_name in config["tools"]:
                tool_def = cls.get_tool_definition(tool_name)
                if tool_def:
                    tools.append(tool_def)
        
        # Create agent instance
        agent = agent_cls(
            agent_id=agent_id,
            name=config.get("name", agent_type),
            description=config.get("description", ""),
            instructions=config.get("instructions", ""),
            tools=tools,
            llm_provider=get_llm_provider(),
            model=config.get("model")
        )
        
        # Store instance
        cls._instances[agent_id] = agent
        
        logger.info(f"Created agent: {agent.name} ({agent_id})")
        return agent
    
    @classmethod
    def get_agent(cls, agent_id: str) -> Optional[AbstractAgent]:
        """
        Get an agent instance by ID
        
        Args:
            agent_id: ID of the agent to get
            
        Returns:
            Agent instance or None if not found
        """
        return cls._instances.get(agent_id)
    
    @classmethod
    def list_agent_types(cls) -> List[str]:
        """
        List available agent types
        
        Returns:
            List of agent type names
        """
        if not cls._initialized:
            cls.initialize()
            
        return list(cls._agent_configs.keys())
    
    @classmethod
    def get_agent_config(cls, agent_type: str) -> Dict[str, Any]:
        """
        Get configuration for an agent type
        
        Args:
            agent_type: Agent type
            
        Returns:
            Agent configuration
            
        Raises:
            ValueError: If agent type is not configured
        """
        if not cls._initialized:
            cls.initialize()
            
        if agent_type not in cls._agent_configs:
            raise ValueError(f"Agent type not configured: {agent_type}")
            
        return cls._agent_configs[agent_type] 