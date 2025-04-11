import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import hashlib

from backend.app.agents.base import AbstractAgent, AgentRequest, AgentResponse, ToolDefinition
from backend.app.llm.provider import LLMProvider

# Setup logger
logger = logging.getLogger("app.agents.implementations.question_generator")

class QuestionGeneratorAgent(AbstractAgent):
    """
    Agent for generating medical questions
    
    This agent specializes in creating high-quality medical questions
    based on the SESATS guidelines.
    """
    
    # Question types based on SESATS guidelines
    QUESTION_TYPES = {
        "clinical_scenario": "Generate a question with a realistic clinical scenario requiring surgical decision-making",
        "diagnostic": "Generate a question focused on diagnosis of surgical conditions",
        "management": "Generate a question about surgical management options",
        "complications": "Generate a question about potential complications and their management",
        "technical": "Generate a question about surgical technical details and procedures",
        "perioperative": "Generate a question about perioperative care and considerations"
    }
    
    # Complexity levels for questions
    COMPLEXITY_LEVELS = {
        "low": "Basic application of principles, suitable for early trainees",
        "medium": "Moderate complexity requiring solid understanding of principles",
        "high": "Complex scenarios requiring deep understanding and advanced decision-making, ensure that all options are plausible and realistic"
    }
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        instructions: str,
        llm_provider: Optional[LLMProvider] = None,
        tools: Optional[List[ToolDefinition]] = None,
        state_enabled: bool = True,
        **kwargs
    ):
        """Initialize with additional caching support"""
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
        # Initialize cache
        self._question_cache = {}
        self.cache_enabled = kwargs.get("cache_enabled", True)
        self.cache_size_limit = kwargs.get("cache_size_limit", 100)
    
    def _get_cache_key(self, request: AgentRequest, question_type: str, complexity: str) -> str:
        """Generate a cache key from request and parameters"""
        # Create a deterministic key from the input parameters
        key_components = [
            request.prompt[:100],  # Use first 100 chars of prompt
            question_type,
            complexity,
            str(request.params.get("temperature", 0.7)),
            str(request.params.get("max_tokens", 1000))
        ]
        return hashlib.md5(":".join(key_components).encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve result from cache if available"""
        if not self.cache_enabled:
            return None
        
        cached_item = self._question_cache.get(cache_key)
        if cached_item:
            logger.info(f"Cache hit for question generator: {cache_key[:8]}")
            return cached_item
        return None
    
    def _add_to_cache(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Add result to cache, respecting size limits"""
        if not self.cache_enabled:
            return
        
        # Implement simple LRU-like cache - remove oldest item if at capacity
        if len(self._question_cache) >= self.cache_size_limit:
            # Remove oldest item (first key)
            if self._question_cache:
                oldest_key = next(iter(self._question_cache))
                self._question_cache.pop(oldest_key)
        
        # Add to cache
        self._question_cache[cache_key] = result
        logger.info(f"Added to question cache: {cache_key[:8]}")
    
    def enhance_prompt_with_question_type(self, prompt: str, question_type: str) -> str:
        """Enhance the prompt with specific question type instructions"""
        if question_type not in self.QUESTION_TYPES:
            logger.warning(f"Unknown question type: {question_type}, using default prompt")
            return prompt
            
        type_instruction = self.QUESTION_TYPES[question_type]
        return f"{prompt}\n\nQuestion Type: {type_instruction}"
    
    def enhance_prompt_with_complexity(self, prompt: str, complexity: str) -> str:
        """Enhance the prompt with complexity level instructions"""
        if complexity not in self.COMPLEXITY_LEVELS:
            logger.warning(f"Unknown complexity level: {complexity}, using default prompt")
            return prompt
            
        complexity_instruction = self.COMPLEXITY_LEVELS[complexity]
        return f"{prompt}\n\nComplexity Level: {complexity_instruction}"
        
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute question generation request with support for types and complexity
        
        Args:
            request: Agent request with prompt and optional parameters:
                    - question_type: Type of question to generate
                    - complexity: Complexity level of the question
                    
        Returns:
            Agent response with generated question
        """
        start_time = datetime.utcnow()
        request = request.with_context()
        
        # Extract question parameters from request
        question_type = request.params.pop("question_type", "clinical_scenario")
        complexity = request.params.pop("complexity", "medium")
        use_cache = request.params.pop("use_cache", self.cache_enabled)
        
        # Enhanced prompt with question type and complexity
        enhanced_prompt = self.enhance_prompt_with_question_type(request.prompt, question_type)
        enhanced_prompt = self.enhance_prompt_with_complexity(enhanced_prompt, complexity)
        
        try:
            # Check cache first if enabled
            if use_cache:
                cache_key = self._get_cache_key(request, question_type, complexity)
                cached_result = self._get_from_cache(cache_key)
                if cached_result:
                    elapsed = (datetime.utcnow() - start_time).total_seconds()
                    return AgentResponse(
                        text=cached_result.get("text", ""),
                        request_id=request.context.request_id,
                        agent_id=self.agent_id,
                        agent_name=self.name,
                        elapsed_time=elapsed,
                        output_data=cached_result.get("output_data", {}),
                        metadata={
                            "model": cached_result.get("model", "unknown"),
                            "cached": True,
                            "question_type": question_type,
                            "complexity": complexity
                        },
                        success=True
                    )
            
            # Add instructions to extract structured JSON from the LLM
            # This ensures the response is formatted correctly
            system_prompt = self.format_system_prompt(request)
            
            # Add a reminder to return JSON
            if "json" not in system_prompt.lower():
                system_prompt += "\n\nReturn your response as a valid JSON object."
            
            # Add SESATS guidelines through system rules integration
            from backend.app.core.system_rules.agent_integration import enhance_question_generator_request
            enhanced_request = enhance_question_generator_request(
                AgentRequest(
                    prompt=enhanced_prompt,
                    system_prompt=system_prompt,
                    context=request.context,
                    params=request.params
                ),
                additional_instructions=(
                    f"Generate a {complexity} complexity {question_type} question "
                    f"following the SESATS guidelines."
                )
            )
            
            result = await self.llm_provider.generate(
                prompt=enhanced_request.prompt,
                system_prompt=enhanced_request.system_prompt,
                **request.params
            )
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            # Extract and parse JSON from response
            text = result.get("text", "")
            output_data = {}
            
            try:
                # Try to extract JSON from the text
                # First, try to parse the whole text as JSON
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
            
            # Add metadata about question type and complexity
            metadata = {
                "model": result.get("model", "unknown"),
                "question_type": question_type,
                "complexity": complexity,
                "cached": False
            }
            
            response = AgentResponse(
                text=text,
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                output_data=output_data,
                metadata=metadata,
                success=result.get("success", False)
            )
            
            if not result.get("success"):
                response.error = result.get("error", "Unknown error")
            else:
                # Add to cache if successful and caching is enabled
                if use_cache:
                    cache_key = self._get_cache_key(request, question_type, complexity)
                    self._add_to_cache(cache_key, {
                        "text": text,
                        "output_data": output_data,
                        "model": result.get("model", "unknown"),
                        "question_type": question_type,
                        "complexity": complexity
                    })
                
            return response
            
        except Exception as e:
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"Error executing agent {self.name}: {str(e)}")
            
            return AgentResponse(
                text=f"Error: {str(e)}",
                request_id=request.context.request_id,
                agent_id=self.agent_id,
                agent_name=self.name,
                elapsed_time=elapsed,
                error=str(e),
                success=False
            ) 