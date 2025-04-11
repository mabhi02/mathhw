"""
API routes for question templates
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import BaseModel, Field

from backend.app.services.question_templates import QuestionTemplateService
from backend.app.dependencies import get_question_template_service

# Create router
router = APIRouter(prefix="/templates", tags=["templates"])

# Models for API
class TemplateInfo(BaseModel):
    """Information about a template"""
    id: str
    type: str
    variables: List[str]
    has_conditionals: bool
    description: Optional[str] = None
    required_variables: Optional[List[str]] = None
    optional_variables: Optional[List[str]] = None

class TemplateTypeInfo(BaseModel):
    """Information about a template type"""
    id: str
    description: str

class TemplateVariables(BaseModel):
    """Variables for template rendering"""
    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary of variable values"
    )

class TemplateCreateRequest(BaseModel):
    """Request to create a new template"""
    template_id: str
    template_type: str
    template_text: str
    metadata: Optional[Dict[str, Any]] = None

class TemplateValidationResult(BaseModel):
    """Result of template variable validation"""
    valid: bool
    missing_required: List[str] = Field(default_factory=list)
    template_id: Optional[str] = None
    error: Optional[str] = None

class TemplateRenderResult(BaseModel):
    """Result of template rendering"""
    stem: Optional[str] = None
    answer_options: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None
    references: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    _metadata: Optional[Dict[str, Any]] = None

@router.get("/", response_model=List[TemplateInfo])
async def get_all_templates(
    service: QuestionTemplateService = Depends(get_question_template_service)
):
    """
    Get all available templates
    
    Returns:
        List of template information
    """
    return service.get_all_templates()

@router.get("/types", response_model=List[TemplateTypeInfo])
async def get_template_types(
    service: QuestionTemplateService = Depends(get_question_template_service)
):
    """
    Get all available template types
    
    Returns:
        List of template type information
    """
    return service.get_available_template_types()

@router.get("/{template_id}", response_model=TemplateInfo)
async def get_template(
    template_id: str,
    service: QuestionTemplateService = Depends(get_question_template_service)
):
    """
    Get template by ID
    
    Args:
        template_id: Template identifier
        
    Returns:
        Template information
    """
    template = service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template not found: {template_id}"
        )
    
    # Get template info in standard format
    templates = service.get_all_templates()
    for t in templates:
        if t["id"] == template_id:
            return t
    
    # Fallback with basic info if not found in get_all_templates
    return {
        "id": template.template_id,
        "type": getattr(template, "template_type", "unknown"),
        "variables": template.get_variables(),
        "has_conditionals": len(template.get_conditionals()) > 0
    }

@router.post("/{template_id}/render", response_model=TemplateRenderResult)
async def render_template(
    template_id: str,
    data: TemplateVariables,
    service: QuestionTemplateService = Depends(get_question_template_service)
):
    """
    Render a template with variables
    
    Args:
        template_id: Template identifier
        data: Variables for rendering
        
    Returns:
        Rendered template result
    """
    # First validate the variables
    validation = service.validate_template_variables(template_id, data.variables)
    if not validation["valid"]:
        missing = validation.get("missing_required", [])
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing required variables: {', '.join(missing)}"
        )
    
    # Render the template
    result = service.render_template(template_id, data.variables)
    
    # Check for errors
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    return result

@router.post("/{template_id}/validate", response_model=TemplateValidationResult)
async def validate_template_variables(
    template_id: str,
    data: TemplateVariables,
    service: QuestionTemplateService = Depends(get_question_template_service)
):
    """
    Validate variables for a template
    
    Args:
        template_id: Template identifier
        data: Variables to validate
        
    Returns:
        Validation results
    """
    validation = service.validate_template_variables(template_id, data.variables)
    
    # Check if template exists
    if "error" in validation and "not found" in validation["error"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=validation["error"]
        )
    
    return validation

@router.post("/", response_model=TemplateInfo, status_code=status.HTTP_201_CREATED)
async def create_template(
    data: TemplateCreateRequest,
    service: QuestionTemplateService = Depends(get_question_template_service)
):
    """
    Create a new template
    
    Args:
        data: Template creation request
        
    Returns:
        Created template information
    """
    result = service.create_template(
        template_text=data.template_text,
        template_id=data.template_id,
        template_type=data.template_type,
        metadata=data.metadata
    )
    
    if not result.get("created", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to create template")
        )
    
    return result

@router.get("/type/{template_type}", response_model=List[TemplateInfo])
async def get_templates_by_type(
    template_type: str,
    service: QuestionTemplateService = Depends(get_question_template_service)
):
    """
    Get templates by type
    
    Args:
        template_type: Type of templates to get
        
    Returns:
        List of matching templates
    """
    templates = service.get_templates_by_type(template_type)
    return templates 