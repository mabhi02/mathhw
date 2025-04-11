import logging
from typing import Dict, Optional
import json
from datetime import datetime

from backend.app.agents.base import AbstractAgent, AgentRequest, AgentResponse

# Setup logger
logger = logging.getLogger("app.agents.implementations.multiple_choice_formatter")

class MultipleChoiceFormatterAgent(AbstractAgent):
    """
    Agent for formatting questions into multiple choice format
    
    This agent specializes in transforming questions into multiple choice format
    with exactly 3 options, following medical education best practices.
    """
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute multiple choice formatting request
        
        Args:
            request: Agent request with question to format
            
        Returns:
            Agent response with formatted multiple choice question
        """
        start_time = datetime.utcnow()
        request = request.with_context()
        
        try:
            system_prompt = self.format_system_prompt(request)
            
            # Ensure the system prompt emphasizes the exact number of options
            if "EXACTLY 3 OPTIONS" not in system_prompt:
                system_prompt += "\n\nIMPORTANT: CREATE EXACTLY 3 OPTIONS ONLY!"
            
            # Add JSON structure reminder
            if "json" not in system_prompt.lower():
                system_prompt += "\n\nReturn your response as a valid JSON object with 'text', 'options', 'explanation', and 'references' fields."
            
            # Process with LLM
            result = await self.llm_provider.generate(
                prompt=f"Format the following question into a multiple choice format:\n\n{request.prompt}",
                system_prompt=system_prompt,
                **request.params
            )
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            # Extract and parse JSON from response
            text = result.get("text", "")
            output_data = {}
            
            try:
                # Try to parse as JSON
                output_data = json.loads(text)
                
                # Validate that we have exactly 3 options
                if "options" in output_data and len(output_data["options"]) != 3:
                    logger.warning(f"Generated {len(output_data['options'])} options instead of exactly 3")
                    
                    # Attempt to fix by trimming or padding
                    if len(output_data["options"]) > 3:
                        output_data["options"] = output_data["options"][:3]
                    elif len(output_data["options"]) < 3:
                        # Pad with empty options if we have too few
                        for i in range(len(output_data["options"]), 3):
                            output_data["options"].append({
                                "text": f"Option {chr(97+i)} needs to be generated",
                                "isCorrect": False
                            })
            except json.JSONDecodeError:
                # If response is not valid JSON, extract what we can
                import re
                
                # Try to find JSON in code blocks
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```|{[\s\S]*}', text)
                if json_match:
                    try:
                        json_str = json_match.group(1) if json_match.group(1) else json_match.group(0)
                        output_data = json.loads(json_str)
                    except (json.JSONDecodeError, IndexError):
                        logger.warning(f"Failed to parse JSON from text: {text}")
                        output_data = {
                            "text": text,
                            "parsing_error": "Could not parse JSON response"
                        }
                else:
                    # Fallback to basic extraction
                    lines = text.strip().split("\n")
                    question_text = lines[0] if lines else ""
                    options = []
                    
                    # Simple heuristic to identify options
                    for line in lines[1:]:
                        if line.strip().startswith(("a)", "b)", "c)", "A.", "B.", "C.")):
                            options.append({
                                "text": line.strip(),
                                "isCorrect": False
                            })
                    
                    output_data = {
                        "text": question_text,
                        "options": options[:3],
                        "parsing_note": "Extracted from non-JSON response"
                    }
            
            return AgentResponse(
                text=result.get("text", ""),
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                output_data=output_data,
                metadata={"model": result.get("model", "unknown")},
                success=result.get("success", False)
            )
            
        except Exception as e:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error executing multiple choice formatter agent {self.name}: {str(e)}")
            
            return AgentResponse(
                text=f"Error formatting multiple choice question: {str(e)}",
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                error=str(e),
                success=False
            ) 