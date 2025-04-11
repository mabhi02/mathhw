from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import uuid

from backend.app.db.base import TimestampedBase

class Question(TimestampedBase):
    """
    Model for storing generated questions
    """
    __tablename__ = "questions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    domain = Column(String(255), nullable=True)
    
    # Metadata about question
    cognitive_complexity = Column(String(50), nullable=True)
    blooms_taxonomy_level = Column(String(50), nullable=True)
    surgically_appropriate = Column(Boolean, nullable=True)
    
    # Relationships
    options = relationship("QuestionOptions", back_populates="question", cascade="all, delete-orphan")
    comparisons = relationship("ComparisonResult", back_populates="question", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question id={self.id} complexity={self.cognitive_complexity}>"


class QuestionOptions(TimestampedBase):
    """
    Model for storing question options (multiple choice)
    """
    __tablename__ = "question_options"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    position = Column(Integer, nullable=False)  # Order of the option (a, b, c)
    
    # Relationship
    question = relationship("Question", back_populates="options")
    
    def __repr__(self):
        return f"<QuestionOption id={self.id} correct={self.is_correct}>" 