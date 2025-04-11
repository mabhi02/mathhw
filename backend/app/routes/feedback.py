from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.crud import user_feedback_crud, comparison_crud
from backend.app.schemas.comparison import UserFeedbackCreate, UserFeedbackResponse

# Create router
router = APIRouter()


@router.get("/{feedback_id}", response_model=UserFeedbackResponse)
def get_feedback(
    feedback_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific user feedback by ID
    """
    feedback = user_feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with ID {feedback_id} not found"
        )
    return feedback


@router.get("/by-comparison/{comparison_id}", response_model=UserFeedbackResponse)
def get_feedback_by_comparison(
    comparison_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user feedback by comparison ID
    """
    feedback = user_feedback_crud.get_by_comparison_id(db, comparison_id=comparison_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No feedback found for comparison with ID {comparison_id}"
        )
    return feedback


@router.post("/", response_model=UserFeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_in: UserFeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Create or update user feedback for a comparison
    """
    # Verify comparison exists
    comparison = comparison_crud.get(db, id=feedback_in.comparison_id)
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comparison with ID {feedback_in.comparison_id} not found"
        )
    
    # Validate preferred output value
    if feedback_in.preferred_output not in ["direct", "agent"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="preferred_output must be either 'direct' or 'agent'"
        )
    
    # Create feedback
    feedback = user_feedback_crud.create_feedback(db, obj_in=feedback_in)
    return feedback


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete user feedback
    """
    feedback = user_feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback with ID {feedback_id} not found"
        )
    user_feedback_crud.remove(db, id=feedback_id)
    return None 