from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid

# Base schemas
class QuestionBase(BaseModel):
    """Base schema for questions"""
    text: str
    explanation: Optional[str] = None
    domain: Optional[str] = None
    cognitive_complexity: Optional[str] = None
    blooms_taxonomy_level: Optional[str] = None
    surgically_appropriate: Optional[bool] = None


class QuestionOptionBase(BaseModel):
    """Base schema for question options"""
    text: str
    is_correct: bool
    position: int


# Creation schemas
class QuestionOptionCreate(QuestionOptionBase):
    """Schema for creating question options"""
    pass


class QuestionCreate(QuestionBase):
    """Schema for creating questions"""
    options: List[QuestionOptionCreate]


# Response schemas
class QuestionOptionResponse(QuestionOptionBase):
    """Schema for question option responses"""
    id: str
    question_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuestionResponse(QuestionBase):
    """Schema for question responses"""
    id: str
    options: List[QuestionOptionResponse]
    created_at: datetime
    updated_at: datetime
    question_type: Optional[str] = None
    outline_id: Optional[str] = None

    model_config = {"from_attributes": True}


# Direct LLM input/output schemas
class DirectQuestionInput(BaseModel):
    """Schema for direct question generation from LLM"""
    prompt: str
    outline: Optional[str] = None
    domain: Optional[str] = None
    complexity: Optional[str] = None


class MultipleChoiceQuestion(BaseModel):
    """Schema for multiple choice questions from LLMs"""
    text: str
    options: List[Dict[str, Any]]
    explanation: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# Advanced API schemas
class QuestionListResponse(BaseModel):
    """Paginated list of questions"""
    items: List[QuestionResponse]
    total: int
    skip: int
    limit: int


class QuestionGenerationInput(BaseModel):
    """Input for generating questions"""
    outline_id: Optional[str] = None
    content: Optional[str] = None
    question_type: Optional[str] = "multiple-choice"
    complexity: Optional[str] = "medium"
    count: Optional[int] = 5
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "outline_id": "abc123",
                "content": "Human anatomy focuses on the study of body structures and their relationships.",
                "question_type": "multiple-choice",
                "complexity": "medium",
                "count": 3
            }
        }
    }


class QuestionGenerationResult(BaseModel):
    """Result of question generation process"""
    questions: List[QuestionResponse]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time: float
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "questions": [],
                "metadata": {
                    "model": "gpt-4",
                    "outline_id": "abc123",
                    "tokens_used": 1250
                },
                "processing_time": 2.5
            }
        }
    }


class BatchQuestionItem(BaseModel):
    """Single item in a batch question request"""
    operation: str = Field(..., description="Operation type: create, update, or delete")
    id: Optional[str] = Field(None, description="Question ID (required for update/delete)")
    data: Optional[Union[QuestionCreate, Dict[str, Any]]] = Field(
        None, description="Question data (required for create/update)"
    )


class BatchQuestionRequest(BaseModel):
    """Batch question processing request"""
    items: List[BatchQuestionItem]
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "operation": "create",
                        "data": {
                            "text": "What is the primary function of the heart?",
                            "domain": "cardiovascular",
                            "options": [
                                {"text": "Pumping blood", "is_correct": True, "position": 0},
                                {"text": "Filtering blood", "is_correct": False, "position": 1}
                            ]
                        }
                    },
                    {
                        "operation": "delete",
                        "id": "question-123"
                    }
                ]
            }
        }
    }


class BatchItemResult(BaseModel):
    """Result of a single batch operation"""
    index: int
    operation: str
    success: bool
    id: Optional[str] = None
    error: Optional[str] = None
    data: Optional[QuestionResponse] = None


class BatchQuestionResponse(BaseModel):
    """Response from batch processing"""
    job_id: Optional[str] = None
    status: str
    message: str
    results: Optional[List[BatchItemResult]] = None 