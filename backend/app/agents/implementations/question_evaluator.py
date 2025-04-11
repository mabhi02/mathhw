import logging
from typing import Dict, List, Optional
import json
from datetime import datetime

from backend.app.agents.base import AbstractAgent, AgentRequest, AgentResponse, ToolDefinition

# Setup logger
logger = logging.getLogger("app.agents.implementations.question_evaluator")

class QuestionEvaluatorAgent(AbstractAgent):
    """
    Agent for evaluating medical questions
    
    This agent specializes in analyzing and improving medical questions
    based on the SESATS guidelines.
    """
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute question evaluation request
        
        Args:
            request: Agent request with question to evaluate
            
        Returns:
            Agent response with evaluation
        """
        # We'll use the tools capability for this agent
        return await self.execute_with_tools(request) 