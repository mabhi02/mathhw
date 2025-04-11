import logging
from typing import Dict, Optional, List
import json
from datetime import datetime

from backend.app.agents.base import AbstractAgent, AgentRequest, AgentResponse, ToolDefinition
from backend.app.core.system_rules.rules import get_system_rules
from backend.app.core.system_rules.validation import validate_against_rules

# Setup logger
logger = logging.getLogger("app.agents.implementations.system_rules")

class SystemRulesAgent(AbstractAgent):
    """
    Agent for managing and applying system rules
    
    This agent specializes in validating content against system rules
    and providing guidance on rule compliance.
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        instructions: str,
        llm_provider: Optional[any] = None,
        tools: Optional[List[ToolDefinition]] = None,
        state_enabled: bool = True,
        **kwargs
    ):
        """Initialize with rule configuration"""
        super().__init__(
            agent_id=agent_id,
            name=name,
            description=description,
            instructions=instructions,
            llm_provider=llm_provider,
            tools=tools,
            state_enabled=state_enabled,
            **kwargs
        )
        # Initialize rules
        self.rules = get_system_rules()
        self.rule_categories = kwargs.get("rule_categories", [])
    
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute system rules validation and application
        
        Args:
            request: Agent request with content to validate or analyze
            
        Returns:
            Agent response with validation results
        """
        start_time = datetime.utcnow()
        request = request.with_context()
        
        try:
            # Extract content to validate
            content = request.prompt
            rule_categories = request.params.get("rule_categories", self.rule_categories)
            
            # Get relevant rules for specified categories
            relevant_rules = self.rules
            if rule_categories:
                relevant_rules = [r for r in self.rules if r.get("category") in rule_categories]
            
            # Validate content against rules
            validation_results = validate_against_rules(content, relevant_rules)
            
            # Enhance system prompt with rules context
            system_prompt = self.format_system_prompt(request)
            system_prompt += "\n\nApply the following system rules in your analysis:\n"
            for rule in relevant_rules:
                system_prompt += f"- {rule.get('name')}: {rule.get('description')}\n"
            
            # Process with LLM for analysis and suggestions
            result = await self.llm_provider.generate(
                prompt=f"Analyze the following content against system rules:\n\n{content}",
                system_prompt=system_prompt,
                **request.params
            )
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            # Prepare output data with validation results
            output_data = {
                "validation_results": validation_results,
                "rules_applied": len(relevant_rules),
                "compliant": all(r.get("compliant", False) for r in validation_results),
                "suggested_improvements": []
            }
            
            # Try to extract structured suggestions from LLM response
            try:
                text = result.get("text", "")
                if "suggestions" in text.lower() or "improvements" in text.lower():
                    lines = text.strip().split("\n")
                    suggestions = [line.strip() for line in lines 
                                  if line.strip() and (line.strip().startswith("-") or 
                                                      line.strip().startswith("*") or
                                                      ":" in line)]
                    output_data["suggested_improvements"] = suggestions
            except Exception as parse_err:
                logger.warning(f"Error parsing suggestions: {str(parse_err)}")
            
            return AgentResponse(
                text=result.get("text", ""),
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                output_data=output_data,
                metadata={
                    "model": result.get("model", "unknown"), 
                    "rules_applied": len(relevant_rules),
                    "rule_categories": rule_categories
                },
                success=result.get("success", False)
            )
            
        except Exception as e:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error executing system rules agent {self.name}: {str(e)}")
            
            return AgentResponse(
                text=f"Error applying system rules: {str(e)}",
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                error=str(e),
                success=False
            ) 