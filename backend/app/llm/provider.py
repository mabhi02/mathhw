import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from functools import lru_cache
import time
from openai import OpenAI, AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.app.config import get_settings

# Setup logger
logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers
    """
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text from prompt
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            Response with text and metadata
        """
        pass
    
    @abstractmethod
    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text from prompt with tools
        
        Args:
            prompt: User prompt
            tools: List of tools
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            Response with text, tool calls, and metadata
        """
        pass


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM provider
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI provider with config
        
        Args:
            config: Provider configuration
        """
        self.api_key = config.get("openai_api_key", os.environ.get("OPENAI_API_KEY"))
        if not self.api_key:
            raise ValueError("OpenAI API key not found in config or environment")
        
        self.model = config.get("model", "gpt-4o")
        self.temperature = config.get("temperature", 0.0)
        self.max_tokens = config.get("max_tokens", 1000)
        self.top_p = config.get("top_p", 1.0)
        self.frequency_penalty = config.get("frequency_penalty", 0.0)
        self.presence_penalty = config.get("presence_penalty", 0.0)
        
        # Support for o1 model which uses max_completion_tokens
        self.max_completion_tokens = config.get("max_completion_tokens")
        
        # System prompts
        self.system_prompts = config.get("system_prompts", {})
        self.default_system_prompt = config.get("system_prompt", "")
        
        # Create client
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        logger.info(f"Initialized OpenAI provider with model: {self.model}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text with OpenAI
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            Response with text and metadata
        """
        start_time = time.time()
        
        # Use provided values or fall back to defaults
        temperature = temperature if temperature is not None else self.temperature
        
        # Handle max_tokens vs max_completion_tokens for different models
        if self.model.startswith("o1"):
            max_completion_tokens = max_tokens if max_tokens is not None else self.max_completion_tokens
            kwargs["max_completion_tokens"] = max_completion_tokens
        else:
            max_tokens_value = max_tokens if max_tokens is not None else self.max_tokens
            kwargs["max_tokens"] = max_tokens_value
        
        # Get system prompt
        if system_prompt is None:
            system_prompt = self.default_system_prompt
        
        messages = [
            {"role": "system", "content": system_prompt} if system_prompt else None,
            {"role": "user", "content": prompt}
        ]
        
        # Remove None values
        messages = [msg for msg in messages if msg]
        
        try:
            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                **kwargs
            )
            
            elapsed_time = time.time() - start_time
            
            # Extract text from response
            text = response.choices[0].message.content or ""
            
            result = {
                "text": text,
                "model": self.model,
                "elapsed_time": elapsed_time,
                "response": response,
                "success": True,
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {str(e)}")
            return {
                "text": f"Error: {str(e)}",
                "model": self.model,
                "elapsed_time": time.time() - start_time,
                "error": str(e),
                "success": False,
            }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_with_tools(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text with OpenAI with tools
        
        Args:
            prompt: User prompt
            tools: List of tools
            system_prompt: Optional system prompt
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            Response with text, tool calls, and metadata
        """
        start_time = time.time()
        
        # Use provided values or fall back to defaults
        temperature = temperature if temperature is not None else self.temperature
        
        # Handle max_tokens vs max_completion_tokens for different models
        if self.model.startswith("o1"):
            max_completion_tokens = max_tokens if max_tokens is not None else self.max_completion_tokens
            kwargs["max_completion_tokens"] = max_completion_tokens
        else:
            max_tokens_value = max_tokens if max_tokens is not None else self.max_tokens
            kwargs["max_tokens"] = max_tokens_value
        
        # Get system prompt
        if system_prompt is None:
            system_prompt = self.default_system_prompt
        
        messages = [
            {"role": "system", "content": system_prompt} if system_prompt else None,
            {"role": "user", "content": prompt}
        ]
        
        # Remove None values
        messages = [msg for msg in messages if msg]
        
        try:
            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                top_p=self.top_p,
                frequency_penalty=self.frequency_penalty,
                presence_penalty=self.presence_penalty,
                tools=tools,
                **kwargs
            )
            
            elapsed_time = time.time() - start_time
            
            # Extract message from response
            message = response.choices[0].message
            
            # Extract tool calls if any
            tool_calls = []
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls = message.tool_calls
            
            result = {
                "text": message.content or "",
                "model": self.model,
                "elapsed_time": elapsed_time,
                "response": response,
                "tool_calls": tool_calls,
                "success": True,
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating text with OpenAI tools: {str(e)}")
            return {
                "text": f"Error: {str(e)}",
                "model": self.model,
                "elapsed_time": time.time() - start_time,
                "error": str(e),
                "success": False,
            }


@lru_cache()
def get_llm_provider() -> LLMProvider:
    """
    Get configured LLM provider
    
    Returns:
        LLM provider instance
    """
    settings = get_settings()
    llm_config = settings.get_llm_config()
    provider_type = llm_config.get("provider", "openai")
    
    if provider_type == "openai":
        # Get the right provider config
        provider_id = llm_config.get("provider", "openai")
        
        # Check if we have specific provider config
        if "providers" in llm_config and provider_id in llm_config["providers"]:
            provider_config = llm_config["providers"][provider_id]
        else:
            # Use root config
            provider_config = llm_config
        
        return OpenAIProvider(provider_config)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_type}") 