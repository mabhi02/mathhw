from typing import Dict, Any, Optional
import logging

from backend.app.core.system_rules.rules import SESATSRules
from backend.app.core.system_rules.prompts import (
    get_question_generator_prompt,
    get_question_evaluator_prompt
)
from backend.app.agents.base import AgentRequest

# Setup logger
logger = logging.getLogger("app.core.system_rules.agent_integration")

def enhance_question_generator_request(
    request: AgentRequest, 
    task_description: Optional[str] = None,
    additional_instructions: str = ""
) -> AgentRequest:
    """
    Enhance a question generator agent request with SESATS guidelines
    
    Args:
        request: Original agent request
        task_description: Task description for the question generator
        additional_instructions: Additional instructions for the question generator
        
    Returns:
        Enhanced agent request
    """
    # Use default task description if not provided
    task_description = task_description or (
        "Create a high-quality multiple-choice question for thoracic surgeons "
        "that follows the SESATS guidelines. The question should require "
        "clinical reasoning and deep understanding of surgical principles."
    )
    
    # Generate enhanced system prompt with SESATS guidelines
    sesats_prompt = get_question_generator_prompt(
        task_description=task_description,
        additional_instructions=additional_instructions
    )
    
    # Create new request with enhanced system prompt
    return AgentRequest(
        prompt=request.prompt,
        system_prompt=sesats_prompt,
        context=request.context,
        params=request.params,
        load_state=request.load_state,
        save_state=request.save_state,
        state_id=request.state_id
    )

def enhance_question_evaluator_request(
    request: AgentRequest,
    evaluation_criteria: Optional[str] = None,
    task_description: Optional[str] = None,
    additional_instructions: str = ""
) -> AgentRequest:
    """
    Enhance a question evaluator agent request with SESATS guidelines
    
    Args:
        request: Original agent request
        evaluation_criteria: Criteria for evaluating the question
        task_description: Task description for the evaluator
        additional_instructions: Additional instructions for the evaluator
        
    Returns:
        Enhanced agent request
    """
    # Use default criteria if not provided
    evaluation_criteria = evaluation_criteria or (
        "Evaluate the question based on:\n"
        "1. Alignment with SESATS guidelines\n"
        "2. Cognitive complexity (recall vs. understanding vs. application)\n"
        "3. Clinical relevance and authenticity\n"
        "4. Quality of response options\n"
        "5. Clarity and conciseness"
    )
    
    # Use default task description if not provided
    task_description = task_description or (
        "Evaluate the given medical question based on the criteria above. "
        "Provide specific feedback on how well it follows SESATS guidelines and "
        "how it could be improved."
    )
    
    # Generate enhanced system prompt with SESATS guidelines
    sesats_prompt = get_question_evaluator_prompt(
        task_description=task_description,
        evaluation_criteria=evaluation_criteria,
        additional_instructions=additional_instructions
    )
    
    # Create new request with enhanced system prompt
    return AgentRequest(
        prompt=request.prompt,
        system_prompt=sesats_prompt,
        context=request.context,
        params=request.params,
        load_state=request.load_state,
        save_state=request.save_state,
        state_id=request.state_id
    )

def get_sesats_system_prompt_for_agent(agent_type: str, **kwargs) -> str:
    """
    Get a SESATS system prompt for a specific agent type
    
    Args:
        agent_type: Type of agent (e.g., "question_generator", "question_evaluator")
        **kwargs: Additional parameters for prompt generation
        
    Returns:
        SESATS system prompt
    """
    if agent_type == "question_generator":
        return get_question_generator_prompt(
            task_description=kwargs.get("task_description", ""),
            additional_instructions=kwargs.get("additional_instructions", "")
        )
    elif agent_type == "question_evaluator":
        return get_question_evaluator_prompt(
            task_description=kwargs.get("task_description", ""),
            evaluation_criteria=kwargs.get("evaluation_criteria", ""),
            additional_instructions=kwargs.get("additional_instructions", "")
        )
    else:
        logger.warning(f"No SESATS system prompt defined for agent type: {agent_type}")
        return "" 