import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
import uuid
import asyncio

from backend.app.agents.base import AbstractAgent, AgentRequest, AgentResponse, AgentContext
from backend.app.agents.factory import AgentFactory

# Setup logger
logger = logging.getLogger("app.agents.pipeline")

class PipelineStep:
    """
    Represents a step in an agent pipeline
    """
    def __init__(
        self, 
        agent_type: str, 
        name: Optional[str] = None,
        description: Optional[str] = None,
        system_prompt: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        use_state: bool = True
    ):
        """
        Initialize pipeline step
        
        Args:
            agent_type: Type of agent to use for this step
            name: Optional name for this step
            description: Optional description
            system_prompt: Optional system prompt override
            params: Optional parameters to pass to the agent
            use_state: Whether to use state persistence for this step
        """
        self.agent_type = agent_type
        self.name = name or f"step_{agent_type}"
        self.description = description or f"Pipeline step using {agent_type} agent"
        self.system_prompt = system_prompt
        self.params = params or {}
        self.agent = None
        self.use_state = use_state
        self.state_id = None
        
    def get_agent(self) -> AbstractAgent:
        """Get or create the agent for this step"""
        if not self.agent:
            self.agent = AgentFactory.create_agent(self.agent_type)
        return self.agent


class PipelineResult:
    """
    Result of a pipeline execution
    """
    def __init__(self, pipeline_id: str):
        """
        Initialize pipeline result
        
        Args:
            pipeline_id: Unique ID for the pipeline
        """
        self.pipeline_id = pipeline_id
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
        self.steps: List[Tuple[str, AgentResponse]] = []
        self.success = True
        self.error: Optional[str] = None
        self.final_response: Optional[AgentResponse] = None
        self.state_ids: Dict[str, str] = {}  # Map of step name to state ID
        
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        end = self.end_time or datetime.utcnow()
        return (end - self.start_time).total_seconds()
    
    def add_step_result(self, step_name: str, response: AgentResponse):
        """
        Add a step result
        
        Args:
            step_name: Name of the pipeline step
            response: Agent response from that step
        """
        self.steps.append((step_name, response))
        
        # Save state ID if present
        if response.state_id:
            self.state_ids[step_name] = response.state_id
        
        # If any step fails, the pipeline fails
        if not response.success:
            self.success = False
            self.error = response.error
        
    def complete(self, final_response: AgentResponse):
        """
        Mark pipeline as complete
        
        Args:
            final_response: Final agent response
        """
        self.end_time = datetime.utcnow()
        self.final_response = final_response
        
        # Log the final response details
        logger.info(f"Pipeline completion - final response success: {final_response.success}")
        logger.info(f"Final response has output_data attr: {hasattr(final_response, 'output_data')}")
        logger.info(f"Final response output_data is None: {final_response.output_data is None if hasattr(final_response, 'output_data') else True}")
        logger.info(f"Final response output_data type: {type(final_response.output_data) if hasattr(final_response, 'output_data') and final_response.output_data is not None else None}")
        logger.info(f"Final response output_data has len: {len(final_response.output_data) if hasattr(final_response, 'output_data') and final_response.output_data is not None and isinstance(final_response.output_data, dict) else 0}")
        
        # Check if output_data exists and is not empty
        has_output_data = (hasattr(final_response, 'output_data') and 
                          final_response.output_data is not None and 
                          isinstance(final_response.output_data, dict) and 
                          len(final_response.output_data) > 0)
                          
        if has_output_data:
            logger.info(f"Final response output_data keys: {final_response.output_data.keys()}")
            
            # Check for questions field specifically
            if 'questions' in final_response.output_data:
                questions = final_response.output_data['questions']
                logger.info(f"Final response contains {len(questions) if questions else 0} questions")
                if not questions:
                    logger.warning("Questions array is empty")
                elif not isinstance(questions, list):
                    logger.warning(f"Questions is not a list but a {type(questions)}")
            else:
                logger.warning("Final response output_data has no 'questions' field")
        else:
            logger.warning("Final response output_data is None or empty")
        
        # Save final state ID
        if final_response.state_id:
            self.state_ids["final"] = final_response.state_id
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "pipeline_id": self.pipeline_id,
            "elapsed_time": self.elapsed_time,
            "success": self.success,
            "error": self.error,
            "steps": [
                {
                    "step": step_name,
                    "agent_id": response.agent_id,
                    "agent_name": response.agent_name,
                    "success": response.success,
                    "elapsed_time": response.elapsed_time,
                    "state_id": response.state_id
                }
                for step_name, response in self.steps
            ],
            "final_output": self.final_response.text if self.final_response else None,
            "final_data": self.final_response.output_data if self.final_response else None,
            "state_ids": self.state_ids
        }


class AgentPipeline:
    """
    Pipeline for executing sequences of agents
    
    The pipeline takes a series of agent steps and executes them in sequence,
    passing the output of each step as input to the next step.
    """
    def __init__(
        self, 
        steps: List[PipelineStep], 
        pipeline_id: Optional[str] = None,
        persistent: bool = True
    ):
        """
        Initialize pipeline
        
        Args:
            steps: List of pipeline steps
            pipeline_id: Optional pipeline ID, generated if not provided
            persistent: Whether to persist state between pipeline runs
        """
        self.steps = steps
        self.pipeline_id = pipeline_id or f"pipeline-{str(uuid.uuid4())[:8]}"
        self.persistent = persistent
        self.state_ids: Dict[str, str] = {}  # Map of step name to state ID
        
        # Ensure all agents are created
        for step in self.steps:
            step.get_agent()
            
        logger.info(f"Initialized pipeline {self.pipeline_id} with {len(steps)} steps")
    
    @classmethod
    def from_config(
        cls, 
        config: Union[List[Dict[str, Any]], str], 
        pipeline_id: Optional[str] = None,
        persistent: bool = True
    ) -> "AgentPipeline":
        """
        Create pipeline from configuration
        
        Args:
            config: List of step configurations or pipeline name
            pipeline_id: Optional pipeline ID
            persistent: Whether to persist state between pipeline runs
            
        Returns:
            Agent pipeline
        """
        # If config is a string, load pipeline configuration from file
        if isinstance(config, str):
            from backend.app.config import get_settings
            settings = get_settings()
            config = settings.get_pipeline_config(config)
            if not config:
                raise ValueError(f"Pipeline configuration not found: {config}")
        
        steps = []
        for step_config in config:
            if "agent_type" not in step_config:
                raise ValueError("Each pipeline step must have an agent_type")
                
            steps.append(PipelineStep(
                agent_type=step_config["agent_type"],
                name=step_config.get("name"),
                description=step_config.get("description"),
                system_prompt=step_config.get("system_prompt"),
                params=step_config.get("params", {}),
                use_state=step_config.get("use_state", True)
            ))
        
        return cls(steps, pipeline_id, persistent)
    
    async def execute(
        self, 
        initial_input: Union[str, Dict[str, Any]], 
        system_prompt: Optional[str] = None,
        continue_from_state: bool = False
    ) -> PipelineResult:
        """
        Execute the pipeline
        
        Args:
            initial_input: Initial prompt or data dictionary to start the pipeline
            system_prompt: Optional system prompt for the first step
            continue_from_state: Whether to continue from saved state
            
        Returns:
            Pipeline result
        """
        if not self.steps:
            raise ValueError("Pipeline has no steps")
        
        result = PipelineResult(self.pipeline_id)
        context = AgentContext(
            request_id=str(uuid.uuid4()),
            trace_id=self.pipeline_id
        )
        
        # Handle input based on type
        if isinstance(initial_input, str):
            current_prompt = initial_input
            current_data = {}
        else:
            # Format the input data as a prompt for the first step
            # Use content field if available, otherwise stringify the data
            current_prompt = initial_input.get("content", str(initial_input))
            current_data = initial_input
        
        # Execute each step in sequence
        for i, step in enumerate(self.steps):
            logger.info(f"Executing pipeline step {i+1}/{len(self.steps)}: {step.name}")
            
            # Determine if we should load state
            load_state = False
            state_id = None
            
            if continue_from_state and self.persistent:
                # Check if we have a saved state for this step
                if step.name in self.state_ids:
                    load_state = True
                    state_id = self.state_ids[step.name]
                    logger.info(f"Continuing from saved state for step {step.name} (ID: {state_id})")
            
            # Merge step params with input data if it's a dictionary
            params = step.params.copy()
            if isinstance(initial_input, dict):
                # Only copy known parameters to avoid flooding the agent with data
                for key in params.keys():
                    if key in current_data:
                        params[key] = current_data[key]
            
            # Create request for this step
            request = AgentRequest(
                prompt=current_prompt,
                system_prompt=step.system_prompt if i > 0 else (system_prompt or step.system_prompt),
                context=context,
                params=params,
                load_state=load_state and step.use_state,
                save_state=self.persistent and step.use_state,
                state_id=state_id
            )
            
            # Execute the agent
            agent = step.get_agent()
            try:
                # Use execute_with_state if available and state is enabled
                if hasattr(agent, 'execute_with_state') and step.use_state:
                    response = await agent.execute_with_state(request)
                else:
                    response = await agent.execute(request)
                    
                result.add_step_result(step.name, response)
                
                # Save state ID for future use
                if response.state_id:
                    self.state_ids[step.name] = response.state_id
                    step.state_id = response.state_id
                
                # If the step failed, stop the pipeline
                if not response.success:
                    logger.error(f"Pipeline step {step.name} failed: {response.error}")
                    result.complete(response)
                    return result
                
                # Update prompt for next step
                current_prompt = response.text
                
                # If this is the last step, complete the pipeline
                if i == len(self.steps) - 1:
                    result.complete(response)
                    
            except Exception as e:
                logger.error(f"Error executing pipeline step {step.name}: {str(e)}")
                error_response = AgentResponse(
                    text=f"Error in pipeline step {step.name}: {str(e)}",
                    request_id=context.request_id,
                    agent_id=agent.agent_id,
                    agent_name=agent.name,
                    elapsed_time=0.0,
                    error=str(e),
                    success=False
                )
                result.add_step_result(step.name, error_response)
                result.complete(error_response)
                break
        
        return result
        
    
# Create a simple helper function to create and execute a pipeline
async def execute_agent_pipeline(
    step_configs: List[Dict[str, Any]], 
    initial_input: Union[str, Dict[str, Any]],
    system_prompt: Optional[str] = None,
    pipeline_id: Optional[str] = None,
    persistent: bool = True,
    continue_from_state: bool = False
) -> Dict[str, Any]:
    """
    Helper function to create and execute a pipeline
    
    Args:
        step_configs: List of step configurations
        initial_input: Initial prompt or data for the pipeline
        system_prompt: Optional system prompt for the first step
        pipeline_id: Optional pipeline ID
        persistent: Whether to persist state between pipeline runs
        continue_from_state: Whether to continue from saved state
        
    Returns:
        Pipeline result as a dictionary
    """
    pipeline = AgentPipeline.from_config(
        step_configs, 
        pipeline_id=pipeline_id, 
        persistent=persistent
    )
    result = await pipeline.execute(
        initial_input=initial_input, 
        system_prompt=system_prompt,
        continue_from_state=continue_from_state
    )
    return result.to_dict() 