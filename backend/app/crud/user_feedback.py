from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid

from backend.app.crud.base import CRUDBase
from backend.app.models.comparison import UserFeedback
from backend.app.schemas.comparison import UserFeedbackCreate, UserFeedbackResponse


class CRUDUserFeedback(CRUDBase[UserFeedback, UserFeedbackCreate, UserFeedbackResponse]):
    """
    CRUD operations for UserFeedback model
    """
    
    def get_by_comparison_id(
        self, db: Session, *, comparison_id: str
    ) -> Optional[UserFeedback]:
        """
        Get user feedback by comparison ID
        
        Args:
            db: SQLAlchemy database session
            comparison_id: Comparison ID to filter by
            
        Returns:
            UserFeedback instance
        """
        return (
            db.query(self.model)
            .filter(self.model.comparison_id == comparison_id)
            .first()
        )
    
    def create_feedback(
        self, db: Session, *, obj_in: UserFeedbackCreate
    ) -> UserFeedback:
        """
        Create user feedback
        
        Args:
            db: SQLAlchemy database session
            obj_in: UserFeedback create schema
            
        Returns:
            Created UserFeedback instance
        """
        # Check if feedback already exists for this comparison
        existing = self.get_by_comparison_id(db, comparison_id=obj_in.comparison_id)
        if existing:
            # Update existing feedback
            for key, value in obj_in.dict().items():
                setattr(existing, key, value)
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        
        # Create new feedback
        obj_in_data = obj_in.dict()
        db_obj = UserFeedback(id=str(uuid.uuid4()), **obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create singleton instance
user_feedback = CRUDUserFeedback(UserFeedback) 