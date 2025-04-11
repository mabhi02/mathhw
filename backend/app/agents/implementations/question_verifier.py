import logging
from typing import Dict, Optional
import json
from datetime import datetime

from backend.app.agents.base import AbstractAgent, AgentRequest, AgentResponse

# Setup logger
logger = logging.getLogger("app.agents.implementations.question_verifier")

class QuestionVerifierAgent(AbstractAgent):
    """
    Agent for verifying medical questions
    
    This agent specializes in validating the quality and cognitive complexity
    of medical questions against professional education standards.
    """
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute question verification request
        
        Args:
            request: Agent request with question to verify
            
        Returns:
            Agent response with verification results
        """
        start_time = datetime.utcnow()
        request = request.with_context()
        
        try:
            system_prompt = self.format_system_prompt(request)
            
            # Add JSON reminder if not present
            if "json" not in system_prompt.lower():
                system_prompt += "\n\nFormat your response as a JSON object with 'verificationResults', 'approved', and 'enhancedMetadata' fields."
            
            # Process with LLM
            result = await self.llm_provider.generate(
                prompt=f"Verify the cognitive complexity and educational quality of this question:\n\n{request.prompt}",
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
                        
                        # Create default verification structure
                        output_data = {
                            "verificationResults": {
                                "clinicalAccuracy": None,
                                "cognitiveComplexity": None,
                                "bloomsLevel": "Unknown",
                                "requiresClinicalReasoning": None
                            },
                            "approved": False,
                            "enhancedMetadata": {
                                "cognitiveComplexity": "Unknown",
                                "bloomsLevel": "Unknown"
                            },
                            "parsing_error": "Could not parse JSON response",
                            "raw_text": text
                        }
            
            # Ensure minimum data structure
            if "verificationResults" not in output_data:
                output_data["verificationResults"] = {}
            if "approved" not in output_data:
                output_data["approved"] = False
            if "enhancedMetadata" not in output_data:
                output_data["enhancedMetadata"] = {}
            
            # Add metadata about verification
            metadata = {
                "model": result.get("model", "unknown"),
                "approved": output_data.get("approved", False),
                "bloom_level": output_data.get("enhancedMetadata", {}).get("bloomsLevel", "Unknown")
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
            logger.error(f"Error executing question verifier agent {self.name}: {str(e)}")
            
            return AgentResponse(
                text=f"Error verifying question: {str(e)}",
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                error=str(e),
                success=False
            ) 