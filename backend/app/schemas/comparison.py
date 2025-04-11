from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# Base schemas
class ComparisonBase(BaseModel):
    """Base schema for comparison results"""
    input_text: str
    direct_output: str
    agent_output: str
    direct_processing_time_ms: Optional[int] = None
    agent_processing_time_ms: Optional[int] = None
    direct_output_data: Optional[Dict[str, Any]] = None
    agent_output_data: Optional[Dict[str, Any]] = None
    agent_steps: Optional[List[Dict[str, Any]]] = None


class UserFeedbackBase(BaseModel):
    """Base schema for user feedback"""
    preferred_output: str = Field(..., description="'direct' or 'agent'")
    rationale: Optional[str] = None
    direct_rating: Optional[int] = Field(None, description="Rating from 1-5")
    agent_rating: Optional[int] = Field(None, description="Rating from 1-5")
    additional_notes: Optional[str] = None


# Create schemas
class ComparisonCreate(ComparisonBase):
    """Schema for creating comparison results"""
    question_id: str


class UserFeedbackCreate(UserFeedbackBase):
    """Schema for creating user feedback"""
    comparison_id: str


# Response schemas
class ComparisonResponse(ComparisonBase):
    """Schema for comparison result responses"""
    id: str
    question_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserFeedbackResponse(UserFeedbackBase):
    """Schema for user feedback responses"""
    id: str
    comparison_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Combined response schema with nested feedback
class ComparisonWithFeedbackResponse(ComparisonResponse):
    """Combined schema with comparison and feedback"""
    user_feedback: Optional[UserFeedbackResponse] = None

    model_config = {"from_attributes": True}


# Input for comparison generation
class ComparisonGenerateInput(BaseModel):
    """Schema for generating comparisons"""
    input_text: str
    domain: Optional[str] = None
    complexity: Optional[str] = None 