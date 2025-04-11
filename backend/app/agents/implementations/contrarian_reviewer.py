import logging
from typing import Dict, Optional
import json
from datetime import datetime

from backend.app.agents.base import AbstractAgent, AgentRequest, AgentResponse

# Setup logger
logger = logging.getLogger("app.agents.implementations.contrarian_reviewer")

class ContrarianReviewerAgent(AbstractAgent):
    """
    Agent for critically reviewing medical questions
    
    This agent specializes in finding flaws and issues in multiple choice questions,
    particularly focusing on cognitive complexity and educational value.
    """
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute contrarian review request
        
        Args:
            request: Agent request with question to review
            
        Returns:
            Agent response with critical review
        """
        start_time = datetime.utcnow()
        request = request.with_context()
        
        try:
            system_prompt = self.format_system_prompt(request)
            
            # Add JSON reminder if not present
            if "json" not in system_prompt.lower():
                system_prompt += "\n\nFormat your response as a JSON object with 'issues' and 'overallAssessment' fields."
            
            # Process with LLM
            result = await self.llm_provider.generate(
                prompt=f"Critically evaluate the following multiple choice question:\n\n{request.prompt}",
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
                        
                        # Fallback: Extract issues manually
                        lines = text.strip().split("\n")
                        issues = []
                        current_issue = {}
                        
                        for line in lines:
                            line = line.strip()
                            if line.startswith(("Issue:", "* Issue:", "- Issue:")):
                                if current_issue and "issue" in current_issue:
                                    issues.append(current_issue)
                                current_issue = {"issue": line.split(":", 1)[1].strip()}
                            elif line.startswith(("Severity:", "* Severity:", "- Severity:")):
                                if current_issue:
                                    current_issue["severity"] = line.split(":", 1)[1].strip()
                            elif line.startswith(("Suggestion:", "* Suggestion:", "- Suggestion:")):
                                if current_issue:
                                    current_issue["suggestion"] = line.split(":", 1)[1].strip()
                        
                        # Add the last issue if it exists
                        if current_issue and "issue" in current_issue:
                            issues.append(current_issue)
                        
                        # Extract overall assessment
                        overall = ""
                        for line in lines:
                            if "overall" in line.lower() or "assessment" in line.lower():
                                parts = line.split(":", 1)
                                if len(parts) > 1:
                                    overall = parts[1].strip()
                                    break
                        
                        output_data = {
                            "issues": issues,
                            "overallAssessment": overall or "Assessment not found in response"
                        }
            
            # Ensure output has minimum structure
            if "issues" not in output_data:
                output_data["issues"] = []
            if "overallAssessment" not in output_data:
                output_data["overallAssessment"] = "No overall assessment provided"
            
            return AgentResponse(
                text=result.get("text", ""),
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                output_data=output_data,
                metadata={"model": result.get("model", "unknown"), "issue_count": len(output_data.get("issues", []))},
                success=result.get("success", False)
            )
            
        except Exception as e:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error executing contrarian reviewer agent {self.name}: {str(e)}")
            
            return AgentResponse(
                text=f"Error reviewing question: {str(e)}",
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                error=str(e),
                success=False
            ) 