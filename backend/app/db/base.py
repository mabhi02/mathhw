from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, func
from datetime import datetime

# Create declarative base for SQLAlchemy models
Base = declarative_base()

# Base model class with common columns
class TimestampedBase(Base):
    """
    Abstract base model with created and updated timestamps
    """
    __abstract__ = True
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    ) 