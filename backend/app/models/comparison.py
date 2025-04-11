from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import uuid

from backend.app.db.base import TimestampedBase

class ComparisonResult(TimestampedBase):
    """
    Model for storing comparison results between direct GPT-4o and agent chain
    """
    __tablename__ = "comparison_results"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    
    # Store raw inputs and outputs
    input_text = Column(Text, nullable=False)  # Original input prompt/question
    direct_output = Column(Text, nullable=False)  # Direct GPT-4o result
    agent_output = Column(Text, nullable=False)  # Agent chain result
    
    # Timing information
    direct_processing_time_ms = Column(Integer, nullable=True)
    agent_processing_time_ms = Column(Integer, nullable=True)
    
    # JSON fields for storing structured data
    direct_output_data = Column(JSON, nullable=True)  # Structured direct output
    agent_output_data = Column(JSON, nullable=True)  # Structured agent output
    agent_steps = Column(JSON, nullable=True)  # Agent process steps
    
    # Relationships
    question = relationship("Question", back_populates="comparisons")
    user_feedback = relationship("UserFeedback", back_populates="comparison", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ComparisonResult id={self.id} question_id={self.question_id}>"


class UserFeedback(TimestampedBase):
    """
    Model for storing user feedback on comparison results
    """
    __tablename__ = "user_feedback"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    comparison_id = Column(String(36), ForeignKey("comparison_results.id"), nullable=False, unique=True)
    
    # User selection
    preferred_output = Column(String(10), nullable=False)  # "direct" or "agent"
    rationale = Column(Text, nullable=True)  # User's rationale for selection
    
    # Optional rating information
    direct_rating = Column(Integer, nullable=True)  # 1-5 rating for direct output
    agent_rating = Column(Integer, nullable=True)  # 1-5 rating for agent output
    
    # Additional feedback
    additional_notes = Column(Text, nullable=True)
    
    # Relationship
    comparison = relationship("ComparisonResult", back_populates="user_feedback")
    
    def __repr__(self):
        return f"<UserFeedback id={self.id} preferred={self.preferred_output}>" 