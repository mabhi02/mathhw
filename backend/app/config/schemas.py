from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class LLMProviderEnum(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    OLLAMA = "ollama"


class SystemPrompts(BaseModel):
    """System prompts for LLM"""
    default: str = ""
    deep_thinking: Optional[str] = None


class LLMProviderConfig(BaseModel):
    """Configuration for a specific LLM provider"""
    provider: LLMProviderEnum
    model: str
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None  # For newer models like o1
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    system_prompts: Optional[SystemPrompts] = None
    system_prompt: Optional[str] = None
    openai_api_key: Optional[str] = None


class LLMConfig(BaseModel):
    """Configuration for LLM generation"""
    provider: LLMProviderEnum
    model: str
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    system_prompts: Optional[SystemPrompts] = None
    system_prompt: Optional[str] = None
    providers: Optional[Dict[str, LLMProviderConfig]] = None


class RedisConfig(BaseModel):
    """Configuration for Redis cache"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    prefix: str = "abts"
    ttl: int = 3600  # Default TTL in seconds
    enabled: bool = True


class SettingsConfig(BaseModel):
    """Root configuration schema for settings.yml"""
    llm: LLMConfig
    redis: Optional[RedisConfig] = None


class ToolParameter(BaseModel):
    """Parameter for an agent tool"""
    name: str
    description: str
    type: str


class ToolDefinition(BaseModel):
    """Definition of a tool an agent can use"""
    name: str
    description: str
    parameters: List[ToolParameter]
    returns: Optional[Dict[str, str]] = None


class AgentDefinition(BaseModel):
    """Definition of an agent"""
    name: str
    model: str
    instructions: str
    tools: Optional[List[str]] = None


class AgentDefinitionsConfig(BaseModel):
    """Root configuration schema for agent_definitions.yml"""
    description: str
    agents: Dict[str, AgentDefinition]
    tools: Optional[Dict[str, ToolDefinition]] = None


class SESATSItem(BaseModel):
    """SESATS item structure"""
    terminology: Dict[str, str]
    components: List[str]
    stem: Dict[str, Any]
    best_practice: Optional[str] = None
    lead_in_examples: Optional[List[str]] = None
    avoid: Optional[List[str]] = None


class SESATSResponseOptions(BaseModel):
    """SESATS response options configuration"""
    structure: List[str]
    rules: List[str]
    formatting_guidelines: List[str]
    trick_avoidance: List[str]


class QuestionRulesConfig(BaseModel):
    """Root configuration schema for question_rules.yml"""
    SESATS_Question_Writing_Guidelines: Dict[str, Any]
    example: Optional[Dict[str, Any]] = None
    
    @field_validator("SESATS_Question_Writing_Guidelines")
    @classmethod
    def validate_guidelines(cls, v):
        # Ensure required fields are present
        required_fields = ["overview", "item_structure", "response_options"]
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required field in guidelines: {field}")
        return v 