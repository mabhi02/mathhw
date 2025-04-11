from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.crud import comparison_crud, question_crud
from backend.app.schemas.comparison import (
    ComparisonCreate,
    ComparisonResponse,
    ComparisonWithFeedbackResponse,
    ComparisonGenerateInput
)

# Create router
router = APIRouter()


@router.get("/", response_model=List[ComparisonResponse])
def get_comparisons(
    question_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get comparison results with optional filtering by question ID
    """
    if question_id:
        comparisons = comparison_crud.get_by_question_id(db, question_id=question_id)
    else:
        comparisons = comparison_crud.get_multi(db, skip=skip, limit=limit)
    return comparisons


@router.get("/{comparison_id}", response_model=ComparisonWithFeedbackResponse)
def get_comparison(
    comparison_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific comparison result by ID with feedback
    """
    comparison = comparison_crud.get_with_feedback(db, id=comparison_id)
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comparison with ID {comparison_id} not found"
        )
    return comparison


@router.post("/", response_model=ComparisonResponse, status_code=status.HTTP_201_CREATED)
def create_comparison(
    comparison_in: ComparisonCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new comparison result
    """
    # Verify question exists
    question = question_crud.get(db, id=comparison_in.question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {comparison_in.question_id} not found"
        )
    
    # Create comparison
    comparison = comparison_crud.create_comparison(db, obj_in=comparison_in)
    return comparison


@router.delete("/{comparison_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comparison(
    comparison_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a comparison result
    """
    comparison = comparison_crud.get(db, id=comparison_id)
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comparison with ID {comparison_id} not found"
        )
    comparison_crud.remove(db, id=comparison_id)
    return None 