from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.db.session import get_db
from backend.app.crud import question as question_crud
from backend.app.schemas.question import (
    QuestionCreate, 
    QuestionResponse,
    DirectQuestionInput,
    MultipleChoiceQuestion,
    BatchQuestionRequest,
    BatchQuestionResponse,
    QuestionListResponse,
    QuestionGenerationInput,
    QuestionGenerationResult
)
from backend.app.services.question_service import QuestionService
from backend.app.agents.factory import AgentFactory
from backend.app.core.logging import get_logger

# Create router
router = APIRouter(
    tags=["questions"]
)
logger = get_logger(__name__)


@router.get("/", response_model=QuestionListResponse)
def get_questions(
    domain: Optional[str] = None,
    complexity: Optional[str] = None,
    question_type: Optional[str] = None,
    outline_id: Optional[str] = None,
    keywords: Optional[List[str]] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get questions with advanced filtering and pagination
    
    - **domain**: Filter by knowledge domain
    - **complexity**: Filter by question complexity (e.g., easy, medium, hard)
    - **question_type**: Filter by question type (e.g., multiple-choice, short-answer)
    - **outline_id**: Filter by the outline ID that generated the questions
    - **keywords**: Filter by keywords in question content
    - **skip**: Number of records to skip for pagination
    - **limit**: Maximum number of records to return
    """
    filters = {
        "domain": domain,
        "complexity": complexity,
        "question_type": question_type,
        "outline_id": outline_id,
        "keywords": keywords
    }
    
    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}
    
    questions = question_crud.get_with_filters(db, filters=filters, skip=skip, limit=limit)
    total = question_crud.count_with_filters(db, filters=filters)
    
    return QuestionListResponse(
        items=questions,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(
    question_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific question by ID
    """
    question = question_crud.get(db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    return question


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    question_in: QuestionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new question with options
    """
    question = question_crud.create_with_options(db, obj_in=question_in)
    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a question
    """
    question = question_crud.get(db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found"
        )
    question_crud.remove(db, id=question_id)
    return None


@router.post("/generate", response_model=QuestionGenerationResult)
async def generate_questions(
    input_data: QuestionGenerationInput,
    db: Session = Depends(get_db)
):
    """
    Generate questions based on input data using the agent pipeline
    
    This endpoint uses the configured agent pipeline to generate questions
    from an outline or specific input text.
    """
    question_service = QuestionService(db)
    try:
        logger.info(f"Starting question generation with input: {input_data.content[:50]}...")
        logger.info(f"Using question type: {input_data.question_type}, complexity: {input_data.complexity}, count: {input_data.count}")
        
        result = await question_service.generate_questions(
            input_data.outline_id, 
            input_data.content,
            input_data.question_type,
            input_data.complexity,
            input_data.count
        )
        return result
    except TypeError as e:
        # Specifically handle TypeError that contains NoneType and iterable to provide better diagnostics
        if "NoneType" in str(e) and "iterable" in str(e):
            logger.error(f"TypeError in question generation: {str(e)}")
            
            # Return empty questions with error metadata
            return QuestionGenerationResult(
                questions=[],
                metadata={
                    "error": str(e),
                    "error_type": "NoneType_not_iterable",
                    "generated_at": datetime.utcnow().isoformat()
                },
                processing_time=0.0
            )
        # For other TypeErrors, re-raise
        else:
            logger.error(f"Unexpected TypeError in question generation: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating questions: {str(e)}"
        )


@router.post("/batch", response_model=BatchQuestionResponse)
async def batch_process_questions(
    batch_request: BatchQuestionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Process a batch of question operations
    
    This endpoint allows for batch creation, updating, or deletion of questions.
    For large batches, processing happens in the background and a job ID is returned.
    """
    question_service = QuestionService(db)
    
    if len(batch_request.items) > 50:  # Process larger batches in background
        job_id = await question_service.create_batch_job(batch_request)
        background_tasks.add_task(
            question_service.process_batch_job,
            job_id,
            batch_request
        )
        return BatchQuestionResponse(
            job_id=job_id,
            status="processing",
            message=f"Processing {len(batch_request.items)} items in the background",
            results=None
        )
    else:  # Process smaller batches immediately
        results = question_service.process_batch(batch_request)
        return BatchQuestionResponse(
            job_id=None,
            status="completed",
            message=f"Processed {len(results)} items",
            results=results
        )


@router.get("/batch/{job_id}", response_model=BatchQuestionResponse)
async def get_batch_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the status of a batch processing job
    """
    question_service = QuestionService(db)
    job_status = await question_service.get_batch_job_status(job_id)
    
    if not job_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch job with ID {job_id} not found"
        )
    
    return job_status


@router.get("/stats", response_model=Dict[str, Any])
def get_question_stats(
    db: Session = Depends(get_db)
):
    """
    Get statistics about the questions in the database
    """
    stats = question_crud.get_statistics(db)
    return stats


@router.post("/generate/preview", response_model=QuestionGenerationResult)
async def generate_questions_preview(
    request: QuestionGenerationInput,
    db: Session = Depends(get_db)
):
    """
    Generate questions without saving to database (preview mode)
    
    Args:
        request: Question generation input
        
    Returns:
        Generated questions result
    """
    question_service = QuestionService(db)
    try:
        logger.info(f"Starting question generation preview with input: {request.content[:50]}...")
        logger.info(f"Using question type: {request.question_type}, complexity: {request.complexity}, count: {request.count}")
        
        # Generate questions but don't save to database
        result = await question_service.generate_questions_preview(
            outline_id=request.outline_id,
            content=request.content,
            question_type=request.question_type,
            complexity=request.complexity,
            count=request.count
        )
        
        return result
    except ValueError as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error generating questions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate questions: {str(e)}"
        )


@router.get("/test-parser", response_model=Dict[str, Any])
async def test_parser():
    """
    Test endpoint for checking the JSON parsing in the final formatter
    
    This is a debugging endpoint to help diagnose issues with JSON parsing
    in the final formatter agent.
    """
    from backend.app.llm import get_llm_provider
    from backend.app.agents.implementations.final_formatter import FinalFormatterAgent
    from backend.app.agents.base import AgentRequest, AgentContext
    import json
    
    # Create a simple test JSON with markdown formatting
    test_json = '''```json
    {
      "text": "This is a test question",
      "options": [
        {
          "text": "Option A",
          "isCorrect": true
        },
        {
          "text": "Option B",
          "isCorrect": false
        },
        {
          "text": "Option C",
          "isCorrect": false
        }
      ],
      "explanation": "This is a test explanation",
      "references": [],
      "metadata": {
        "cognitiveComplexity": "Medium",
        "bloomsLevel": "Application"
      }
    }
    ```'''
    
    # Create the final formatter agent
    agent = FinalFormatterAgent(
        agent_id="test-formatter",
        name="Test Formatter",
        description="Test formatter agent",
        instructions="Test instructions"
    )
    
    # Create a request
    request = AgentRequest(
        prompt=test_json,
        context=AgentContext()
    )
    
    # Execute the agent
    response = await agent.execute(request)
    
    # Return the result
    return {
        "success": response.success,
        "text": response.text[:100] + "...",
        "has_output_data": response.output_data is not None,
        "output_data_keys": list(response.output_data.keys()) if response.output_data else [],
        "has_questions": "questions" in response.output_data if response.output_data else False,
        "questions_count": len(response.output_data.get("questions", [])) if response.output_data else 0,
        "questions": response.output_data.get("questions", []) if response.output_data else []
    } 