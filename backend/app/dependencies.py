"""
Dependencies for FastAPI
"""
from typing import Generator
import logging

from backend.app.services.question_templates import QuestionTemplateService
from backend.app.services.outlines import OutlineService

# Setup logger
logger = logging.getLogger("app.dependencies")

# Singleton instances
_question_template_service = None
_outline_service = None

def get_question_template_service() -> QuestionTemplateService:
    """
    Get or create QuestionTemplateService instance
    
    Returns:
        QuestionTemplateService instance
    """
    global _question_template_service
    
    if _question_template_service is None:
        logger.info("Creating QuestionTemplateService instance")
        _question_template_service = QuestionTemplateService()
    
    return _question_template_service

def get_outline_service() -> OutlineService:
    """
    Get or create OutlineService instance
    
    Returns:
        OutlineService instance
    """
    global _outline_service
    
    if _outline_service is None:
        logger.info("Creating OutlineService instance")
        _outline_service = OutlineService()
    
    return _outline_service 