import logging
from typing import Dict, Optional, List
import json
from datetime import datetime

from backend.app.agents.base import AbstractAgent, AgentRequest, AgentResponse

# Setup logger
logger = logging.getLogger("app.agents.implementations.surgical_situation_validator")

class SurgicalSituationValidatorAgent(AbstractAgent):
    """
    Agent for validating surgical clinical scenarios
    
    This agent specializes in ensuring that medical questions present
    realistic surgical scenarios that require appropriate clinical decision-making.
    """
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute surgical scenario validation request
        
        Args:
            request: Agent request with surgical scenario to validate
            
        Returns:
            Agent response with validation results
        """
        start_time = datetime.utcnow()
        request = request.with_context()
        
        try:
            system_prompt = self.format_system_prompt(request)
            
            # Add JSON reminder if not present
            if "json" not in system_prompt.lower():
                system_prompt += "\n\nFormat your response as a JSON object with 'validationResults', 'surgicallyAppropriate', 'suggestedImprovements', and 'improvedScenario' fields."
            
            # Process with LLM
            result = await self.llm_provider.generate(
                prompt=f"Validate the following surgical clinical scenario for realism and appropriateness:\n\n{request.prompt}",
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
                        
                        # Extract structured data from plain text
                        validation_results = {}
                        suggestions = []
                        improved_scenario = ""
                        
                        lines = text.strip().split("\n")
                        for line in lines:
                            line = line.strip().lower()
                            
                            # Extract validation results
                            if "realistic" in line:
                                validation_results["isRealisticSituation"] = "yes" in line or "true" in line
                            if "decision point" in line or "contains decision" in line:
                                validation_results["containsDecisionPoint"] = "yes" in line or "true" in line
                            if "necessary details" in line or "required details" in line:
                                validation_results["hasNecessaryDetails"] = "yes" in line or "true" in line
                            if "irrelevant" in line:
                                validation_results["excludesIrrelevantDetails"] = "yes" in line or "true" in line
                            if "best practice" in line:
                                validation_results["followsBestPractices"] = "yes" in line or "true" in line
                            if "surgical decision" in line:
                                validation_results["requiresSurgicalDecision"] = "yes" in line or "true" in line
                            
                            # Extract suggestions
                            if "suggestion" in line or "improve" in line:
                                if ":" in line:
                                    suggestion = line.split(":", 1)[1].strip()
                                    suggestions.append(suggestion)
                            
                            # Check if this might be the improved scenario
                            if "improved scenario" in line or "corrected scenario" in line:
                                start_idx = lines.index(line)
                                if start_idx < len(lines) - 1:
                                    improved_scenario = "\n".join(lines[start_idx+1:])
                        
                        # Create structured output
                        output_data = {
                            "validationResults": validation_results,
                            "surgicallyAppropriate": all(validation_results.values()) if validation_results else False,
                            "suggestedImprovements": suggestions,
                            "improvedScenario": improved_scenario,
                            "parsing_error": "Extracted from non-JSON response",
                            "raw_text": text
                        }
            
            # Ensure minimum data structure
            if "validationResults" not in output_data:
                output_data["validationResults"] = {}
            if "surgicallyAppropriate" not in output_data:
                output_data["surgicallyAppropriate"] = False
            if "suggestedImprovements" not in output_data:
                output_data["suggestedImprovements"] = []
            if "improvedScenario" not in output_data:
                output_data["improvedScenario"] = ""
            
            # Add metadata about validation
            metadata = {
                "model": result.get("model", "unknown"),
                "surgically_appropriate": output_data.get("surgicallyAppropriate", False),
                "improvement_count": len(output_data.get("suggestedImprovements", []))
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
            logger.error(f"Error executing surgical situation validator agent {self.name}: {str(e)}")
            
            return AgentResponse(
                text=f"Error validating surgical scenario: {str(e)}",
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                error=str(e),
                success=False
            ) 