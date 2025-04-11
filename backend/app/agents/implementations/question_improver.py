import logging
from typing import Dict, Optional
import json
from datetime import datetime

from backend.app.agents.base import AbstractAgent, AgentRequest, AgentResponse

# Setup logger
logger = logging.getLogger("app.agents.implementations.question_improver")

class QuestionImproverAgent(AbstractAgent):
    """
    Agent for improving medical questions
    
    This agent specializes in enhancing questions to increase cognitive complexity
    and improve educational value by requiring deeper clinical reasoning.
    """
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute question improvement request
        
        Args:
            request: Agent request with question to improve
            
        Returns:
            Agent response with improved question
        """
        start_time = datetime.utcnow()
        request = request.with_context()
        
        try:
            system_prompt = self.format_system_prompt(request)
            
            # Add JSON reminder if not present
            if "json" not in system_prompt.lower():
                system_prompt += "\n\nFormat your response as a complete JSON object following the multiple choice question structure."
            
            # Process with LLM
            result = await self.llm_provider.generate(
                prompt=f"Improve the following question to require deeper clinical reasoning:\n\n{request.prompt}",
                system_prompt=system_prompt,
                **request.params
            )
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            # Extract and parse JSON from response
            text = result.get("text", "")
            output_data = {}
            
            try:
                # Try to parse the whole text as JSON
                output_data = json.loads(text)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON with regex
                import re
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```|{[\s\S]*}', text)
                if json_match:
                    try:
                        json_str = json_match.group(1) if json_match.group(1) else json_match.group(0)
                        output_data = json.loads(json_str)
                    except (json.JSONDecodeError, IndexError):
                        logger.warning(f"Failed to parse JSON from text: {text}")
                        
                        # Return the raw text as the response
                        output_data = {
                            "text": text,
                            "parsing_error": "Could not parse JSON response"
                        }
            
            # Add metadata about improvement
            metadata = {
                "model": result.get("model", "unknown"),
                "improved": True
            }
            
            return AgentResponse(
                text=text,
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                output_data=output_data,
                metadata=metadata,
                success=result.get("success", False)
            )
            
        except Exception as e:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error executing question improver agent {self.name}: {str(e)}")
            
            return AgentResponse(
                text=f"Error improving question: {str(e)}",
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                error=str(e),
                success=False
            ) 