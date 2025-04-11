from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import uuid

from backend.app.crud.base import CRUDBase
from backend.app.models.comparison import ComparisonResult
from backend.app.schemas.comparison import ComparisonCreate, ComparisonResponse


class CRUDComparison(CRUDBase[ComparisonResult, ComparisonCreate, ComparisonResponse]):
    """
    CRUD operations for ComparisonResult model
    """
    
    def get_by_question_id(
        self, db: Session, *, question_id: str
    ) -> List[ComparisonResult]:
        """
        Get comparison results by question ID
        
        Args:
            db: SQLAlchemy database session
            question_id: Question ID to filter by
            
        Returns:
            List of ComparisonResult instances
        """
        return (
            db.query(self.model)
            .filter(self.model.question_id == question_id)
            .all()
        )
    
    def get_with_feedback(
        self, db: Session, *, id: str
    ) -> Optional[ComparisonResult]:
        """
        Get comparison result with user feedback
        
        Args:
            db: SQLAlchemy database session
            id: Comparison ID
            
        Returns:
            ComparisonResult instance with user_feedback relationship loaded
        """
        return (
            db.query(self.model)
            .filter(self.model.id == id)
            .first()
        )
    
    def create_comparison(
        self, db: Session, *, obj_in: ComparisonCreate
    ) -> ComparisonResult:
        """
        Create a comparison result
        
        Args:
            db: SQLAlchemy database session
            obj_in: Comparison create schema
            
        Returns:
            Created ComparisonResult instance
        """
        obj_in_data = obj_in.dict()
        db_obj = ComparisonResult(id=str(uuid.uuid4()), **obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create singleton instance
comparison = CRUDComparison(ComparisonResult) 