"""
Models for medical education outlines
"""
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator

class OutlineNodeType(str, Enum):
    """Types of nodes in an outline structure"""
    SECTION = "section"
    TOPIC = "topic"
    SUBTOPIC = "subtopic" 
    CONCEPT = "concept"
    OBJECTIVE = "objective"
    POINT = "point"
    QUESTION = "question"
    ROOT = "root"

class OutlineMetadata(BaseModel):
    """Metadata for an outline or outline node"""
    domain: Optional[str] = None
    complexity: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    sesats_category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class OutlineNode(BaseModel):
    """
    Node in an outline structure
    
    Represents a hierarchical element in a medical education outline.
    Each node can have children, forming a tree structure.
    """
    id: str
    title: str
    type: OutlineNodeType
    content: Optional[str] = None
    children: List["OutlineNode"] = Field(default_factory=list)
    metadata: OutlineMetadata = Field(default_factory=OutlineMetadata)
    parent_id: Optional[str] = None
    
    @field_validator("id")
    @classmethod
    def id_must_be_valid(cls, v):
        """Validate that ID is non-empty"""
        if not v or not v.strip():
            raise ValueError("ID cannot be empty")
        return v.strip()
    
    @field_validator("title")
    @classmethod
    def title_must_be_valid(cls, v):
        """Validate that title is non-empty"""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
        
    def add_child(self, child: "OutlineNode") -> None:
        """
        Add a child node
        
        Args:
            child: Child node to add
        """
        child.parent_id = self.id
        self.children.append(child)
    
    def find_node_by_id(self, node_id: str) -> Optional["OutlineNode"]:
        """
        Find a node by ID in this node or its descendants
        
        Args:
            node_id: ID to search for
            
        Returns:
            Matching node or None if not found
        """
        if self.id == node_id:
            return self
            
        for child in self.children:
            result = child.find_node_by_id(node_id)
            if result:
                return result
                
        return None
    
    def get_depth(self) -> int:
        """
        Get the depth of this node in the hierarchy
        
        Returns:
            Depth (0 for root)
        """
        if not self.parent_id:
            return 0
            
        depth = 0
        current = self
        
        while current.parent_id:
            depth += 1
            current = current.parent
            
        return depth
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert node to dictionary representation
        
        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "content": self.content,
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata.dict(exclude_none=True)
        }

class Outline(BaseModel):
    """
    Complete outline structure
    
    Represents a full medical education outline with metadata and
    hierarchical content.
    """
    id: str
    title: str
    description: Optional[str] = None
    root: OutlineNode
    metadata: OutlineMetadata = Field(default_factory=OutlineMetadata)
    
    def find_node_by_id(self, node_id: str) -> Optional[OutlineNode]:
        """
        Find a node by ID in the outline
        
        Args:
            node_id: ID to search for
            
        Returns:
            Matching node or None if not found
        """
        return self.root.find_node_by_id(node_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert outline to dictionary representation
        
        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "root": self.root.to_dict(),
            "metadata": self.metadata.dict(exclude_none=True)
        }
        
    @classmethod
    def create_empty(cls, id: str, title: str) -> "Outline":
        """
        Create an empty outline with just a root node
        
        Args:
            id: Outline ID
            title: Outline title
            
        Returns:
            Empty outline
        """
        root = OutlineNode(
            id=f"{id}_root",
            title=title,
            type=OutlineNodeType.ROOT
        )
        
        return cls(
            id=id,
            title=title,
            root=root
        ) 