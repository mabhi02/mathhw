from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
import uuid
from datetime import datetime, timedelta
import logging

from backend.app.crud.base import CRUDBase
from backend.app.models.question import Question, QuestionOptions
from backend.app.schemas.question import QuestionCreate, QuestionResponse


class CRUDQuestion(CRUDBase[Question, QuestionCreate, QuestionResponse]):
    """
    CRUD operations for Question model
    """
    
    def create_with_options(
        self, db: Session, *, obj_in: QuestionCreate
    ) -> Question:
        """
        Create a question with its options
        
        Args:
            db: SQLAlchemy database session
            obj_in: Question create schema with options
            
        Returns:
            Created Question instance
        """
        logger = logging.getLogger("app.crud.question")
        
        # Log inputs
        logger.info(f"Creating question with options: {obj_in.text[:50]}...")
        logger.info(f"Number of options: {len(obj_in.options)}")
        
        try:
            # Extract options data
            options_data = obj_in.options
            logger.info(f"Options data type: {type(options_data)}")
            
            # Log options
            for i, opt in enumerate(options_data):
                logger.info(f"Option {i+1}: {opt.text[:30]}... is_correct={opt.is_correct}")
                
            obj_in_data = obj_in.dict(exclude={"options"})
            
            # Create question
            question_id = str(uuid.uuid4())
            db_obj = Question(id=question_id, **obj_in_data)
            db.add(db_obj)
            logger.info(f"Added question to session: {question_id}")
            
            # Create options
            for i, option in enumerate(options_data):
                option_data = option.dict()
                logger.info(f"Creating option: {option_data}")
                
                db_option = QuestionOptions(
                    id=str(uuid.uuid4()),
                    question_id=question_id,
                    position=option_data.get("position", i),
                    **{k: v for k, v in option_data.items() if k != "position"}
                )
                db.add(db_option)
            
            # Commit the transaction
            logger.info("Committing transaction...")
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Successfully created question with ID: {db_obj.id}")
            
            return db_obj
        except Exception as e:
            logger.error(f"Error creating question with options: {str(e)}", exc_info=True)
            db.rollback()
            raise
    
    def get_by_domain(
        self, db: Session, *, domain: str, skip: int = 0, limit: int = 100
    ) -> List[Question]:
        """
        Get questions by domain
        
        Args:
            db: SQLAlchemy database session
            domain: Domain to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Question instances
        """
        return (
            db.query(self.model)
            .filter(self.model.domain == domain)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_complexity(
        self, db: Session, *, complexity: str, skip: int = 0, limit: int = 100
    ) -> List[Question]:
        """
        Get questions by cognitive complexity
        
        Args:
            db: SQLAlchemy database session
            complexity: Complexity level to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Question instances
        """
        return (
            db.query(self.model)
            .filter(self.model.cognitive_complexity == complexity)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_with_filters(
        self, db: Session, *, filters: Dict[str, Any], skip: int = 0, limit: int = 100
    ) -> List[Question]:
        """
        Get questions with multiple filters
        
        Args:
            db: SQLAlchemy database session
            filters: Dictionary of filters to apply
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Question instances
        """
        query = db.query(self.model)
        
        # Apply filters
        if "domain" in filters:
            query = query.filter(self.model.domain == filters["domain"])
            
        if "complexity" in filters:
            query = query.filter(self.model.cognitive_complexity == filters["complexity"])
            
        if "question_type" in filters:
            query = query.filter(self.model.question_type == filters["question_type"])
            
        if "outline_id" in filters:
            query = query.filter(self.model.outline_id == filters["outline_id"])
            
        if "keywords" in filters and filters["keywords"]:
            # Search for keywords in question text
            keyword_filters = []
            for keyword in filters["keywords"]:
                keyword_filters.append(self.model.text.ilike(f"%{keyword}%"))
            
            if keyword_filters:
                query = query.filter(or_(*keyword_filters))
        
        return query.offset(skip).limit(limit).all()
    
    def count_with_filters(self, db: Session, *, filters: Dict[str, Any]) -> int:
        """
        Count questions matching the given filters
        
        Args:
            db: SQLAlchemy database session
            filters: Dictionary of filters to apply
            
        Returns:
            Count of matching questions
        """
        query = db.query(func.count(self.model.id))
        
        # Apply filters (same logic as get_with_filters)
        if "domain" in filters:
            query = query.filter(self.model.domain == filters["domain"])
            
        if "complexity" in filters:
            query = query.filter(self.model.cognitive_complexity == filters["complexity"])
            
        if "question_type" in filters:
            query = query.filter(self.model.question_type == filters["question_type"])
            
        if "outline_id" in filters:
            query = query.filter(self.model.outline_id == filters["outline_id"])
            
        if "keywords" in filters and filters["keywords"]:
            # Search for keywords in question text
            keyword_filters = []
            for keyword in filters["keywords"]:
                keyword_filters.append(self.model.text.ilike(f"%{keyword}%"))
            
            if keyword_filters:
                query = query.filter(or_(*keyword_filters))
        
        return query.scalar()
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get statistics about questions in the database
        
        Args:
            db: SQLAlchemy database session
            
        Returns:
            Dictionary of statistics
        """
        # Total number of questions
        total_count = db.query(func.count(self.model.id)).scalar()
        
        # Count by domain
        domain_counts = db.query(
            self.model.domain, func.count(self.model.id)
        ).group_by(self.model.domain).all()
        
        # Count by complexity
        complexity_counts = db.query(
            self.model.cognitive_complexity, func.count(self.model.id)
        ).group_by(self.model.cognitive_complexity).all()
        
        # Count by question type
        type_counts = db.query(
            self.model.question_type, func.count(self.model.id)
        ).group_by(self.model.question_type).all()
        
        # Questions created in the last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_count = db.query(func.count(self.model.id)).filter(
            self.model.created_at >= week_ago
        ).scalar()
        
        return {
            "total_questions": total_count,
            "domains": {domain: count for domain, count in domain_counts if domain},
            "complexity_levels": {level: count for level, count in complexity_counts if level},
            "question_types": {qtype: count for qtype, count in type_counts if qtype},
            "created_last_7_days": recent_count,
            "updated_at": datetime.utcnow().isoformat()
        }


# Create singleton instance
question = CRUDQuestion(Question) 