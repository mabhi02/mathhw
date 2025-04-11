"""
API routes for outlines
"""
from typing import List, Dict, Optional, Any, Union
from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File, Form
from pydantic import BaseModel, Field

from backend.app.services.outlines import OutlineService
from backend.app.dependencies import get_outline_service
from backend.app.core.outlines import OutlineFormat, OutlineMetadata, OutlineNodeType

# Create router
router = APIRouter(tags=["outlines"])

# Models for API
class OutlineMetadataModel(BaseModel):
    """Metadata for an outline"""
    domain: Optional[str] = None
    complexity: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    sesats_category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class OutlineNodeModel(BaseModel):
    """Node in an outline"""
    id: str
    title: str
    type: str
    content: Optional[str] = None
    children: List["OutlineNodeModel"] = Field(default_factory=list)
    metadata: Optional[OutlineMetadataModel] = None
    parent_id: Optional[str] = None

class OutlineModel(BaseModel):
    """Complete outline structure"""
    id: str
    title: str
    description: Optional[str] = None
    root: OutlineNodeModel
    metadata: Optional[OutlineMetadataModel] = None

class OutlineCreateRequest(BaseModel):
    """Request to create a new outline"""
    content: str
    format: str = "markdown"
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class OutlineListItem(BaseModel):
    """Basic outline information for listing"""
    id: str
    title: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ValidationResult(BaseModel):
    """Result of outline validation"""
    valid: bool
    issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    stats: Dict[str, int] = Field(default_factory=dict)

@router.get("/", response_model=List[OutlineListItem])
async def list_outlines(
    service: OutlineService = Depends(get_outline_service)
):
    """
    List all available outlines
    
    Returns:
        List of outline information
    """
    return service.list_outlines()

@router.post("/", response_model=OutlineModel, status_code=status.HTTP_201_CREATED)
async def create_outline(
    data: OutlineCreateRequest,
    service: OutlineService = Depends(get_outline_service)
):
    """
    Create a new outline
    
    Args:
        data: Outline creation request
        
    Returns:
        Created outline
    """
    try:
        # Parse outline
        outline = service.create_outline(
            content=data.content,
            format=data.format,
            title=data.title,
            metadata=data.metadata
        )
        
        # Save outline
        service.save_outline(outline)
        
        # Convert to API model
        return outline
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating outline: {str(e)}"
        )

@router.post("/upload", response_model=OutlineModel, status_code=status.HTTP_201_CREATED)
async def upload_outline(
    file: UploadFile = File(...),
    format: str = Form("markdown"),
    title: Optional[str] = Form(None),
    service: OutlineService = Depends(get_outline_service)
):
    """
    Upload an outline file
    
    Args:
        file: Outline file to upload
        format: Format of the file
        title: Optional title
        
    Returns:
        Created outline
    """
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode("utf-8")
        
        # Use filename as title if not provided
        if not title and file.filename:
            title = file.filename.split('.')[0]
        
        # Parse outline
        outline = service.create_outline(
            content=content_str,
            format=format,
            title=title
        )
        
        # Save outline
        service.save_outline(outline)
        
        # Convert to API model
        return outline
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error uploading outline: {str(e)}"
        )

@router.get("/{outline_id}", response_model=OutlineModel)
async def get_outline(
    outline_id: str,
    service: OutlineService = Depends(get_outline_service)
):
    """
    Get outline by ID
    
    Args:
        outline_id: Outline ID
        
    Returns:
        Outline details
    """
    outline = service.load_outline(outline_id)
    
    if not outline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outline not found: {outline_id}"
        )
    
    return outline

@router.delete("/{outline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outline(
    outline_id: str,
    service: OutlineService = Depends(get_outline_service)
):
    """
    Delete outline by ID
    
    Args:
        outline_id: Outline ID
    """
    result = service.delete_outline(outline_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outline not found: {outline_id}"
        )

@router.post("/{outline_id}/validate", response_model=ValidationResult)
async def validate_outline(
    outline_id: str,
    service: OutlineService = Depends(get_outline_service)
):
    """
    Validate outline against SESATS standards
    
    Args:
        outline_id: Outline ID
        
    Returns:
        Validation results
    """
    outline = service.load_outline(outline_id)
    
    if not outline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outline not found: {outline_id}"
        )
    
    validation = service.validate_outline(outline)
    return validation

@router.post("/{outline_id}/node/{node_id}/question")
async def create_question_from_node(
    outline_id: str,
    node_id: str,
    template_id: Optional[str] = None,
    service: OutlineService = Depends(get_outline_service)
):
    """
    Create a question from a specific outline node
    
    Args:
        outline_id: Outline ID
        node_id: Node ID
        template_id: Optional template ID to use
        
    Returns:
        Created question
    """
    outline = service.load_outline(outline_id)
    
    if not outline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outline not found: {outline_id}"
        )
    
    node = service.get_node_by_id(outline, node_id)
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Node not found: {node_id}"
        )
    
    result = service.create_question_from_node(node, template_id)
    return result 