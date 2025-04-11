"""
Service for outline management
"""
from typing import Dict, List, Optional, Any, Union
import logging
import uuid
import json
import os
from pathlib import Path

from backend.app.core.outlines import (
    Outline, OutlineNode, OutlineNodeType, OutlineMetadata,
    OutlineParser, OutlineFormat
)
from backend.app.core.system_rules.rules import SESATSRules
from backend.app.config import get_settings

# Setup logger
logger = logging.getLogger("app.services.outlines")

class OutlineService:
    """
    Service for outline management
    
    This service provides high-level operations for working with outlines,
    including parsing, validation, and storage.
    """
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize outline service
        
        Args:
            storage_dir: Directory for outline storage
        """
        settings = get_settings()
        self.storage_dir = storage_dir or Path(settings.STORAGE_DIR) / "outlines"
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.parser = OutlineParser()
        self.sesats_rules = SESATSRules()
    
    def create_outline(self, 
                     content: str, 
                     format: Union[OutlineFormat, str] = OutlineFormat.MARKDOWN,
                     title: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> Outline:
        """
        Create an outline from content
        
        Args:
            content: Outline content
            format: Format of the content
            title: Optional title
            metadata: Optional metadata
            
        Returns:
            Created Outline object
        """
        # Convert string format to enum
        if isinstance(format, str):
            format = OutlineFormat(format)
        
        # Parse outline content
        outline = self.parser.parse(content, format, title, metadata)
        
        return outline
    
    def save_outline(self, outline: Outline) -> str:
        """
        Save outline to storage
        
        Args:
            outline: Outline to save
            
        Returns:
            Path to saved outline
        """
        # Create filename
        filename = f"{outline.id}.json"
        filepath = self.storage_dir / filename
        
        # Convert to dictionary
        data = outline.to_dict()
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved outline to {filepath}")
        return str(filepath)
    
    def load_outline(self, outline_id: str) -> Optional[Outline]:
        """
        Load outline from storage
        
        Args:
            outline_id: ID of outline to load
            
        Returns:
            Loaded Outline object or None if not found
        """
        # Look for file
        filepath = self.storage_dir / f"{outline_id}.json"
        
        if not os.path.exists(filepath):
            logger.warning(f"Outline file not found: {filepath}")
            return None
        
        try:
            # Load from file
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Create root node first
            root_data = data.get("root", {})
            root = self._create_node_from_dict(root_data)
            
            # Create outline
            outline = Outline(
                id=data.get("id", outline_id),
                title=data.get("title", "Untitled Outline"),
                description=data.get("description"),
                root=root,
                metadata=OutlineMetadata(**(data.get("metadata", {}) or {}))
            )
            
            return outline
            
        except Exception as e:
            logger.error(f"Error loading outline {outline_id}: {e}")
            return None
    
    def _create_node_from_dict(self, data: Dict[str, Any]) -> OutlineNode:
        """
        Create a node from dictionary data
        
        Args:
            data: Dictionary data
            
        Returns:
            Created node
        """
        # Create node
        node = OutlineNode(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", "Untitled"),
            type=OutlineNodeType(data.get("type", "section")),
            content=data.get("content"),
            metadata=OutlineMetadata(**(data.get("metadata", {}) or {})),
            parent_id=data.get("parent_id")
        )
        
        # Parse children
        for child_data in data.get("children", []):
            child = self._create_node_from_dict(child_data)
            node.add_child(child)
        
        return node
    
    def delete_outline(self, outline_id: str) -> bool:
        """
        Delete outline from storage
        
        Args:
            outline_id: ID of outline to delete
            
        Returns:
            True if successful
        """
        # Look for file
        filepath = self.storage_dir / f"{outline_id}.json"
        
        if not os.path.exists(filepath):
            logger.warning(f"Outline file not found: {filepath}")
            return False
        
        try:
            # Delete file
            os.remove(filepath)
            logger.info(f"Deleted outline {outline_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting outline {outline_id}: {e}")
            return False
    
    def list_outlines(self) -> List[Dict[str, Any]]:
        """
        List all available outlines
        
        Returns:
            List of outline metadata
        """
        result = []
        
        try:
            # List files in storage directory
            for file in os.listdir(self.storage_dir):
                if file.endswith(".json"):
                    try:
                        # Extract outline ID from filename
                        outline_id = file[:-5]  # Remove '.json'
                        
                        # Load basic metadata
                        with open(os.path.join(self.storage_dir, file), 'r') as f:
                            data = json.load(f)
                        
                        # Add to result
                        result.append({
                            "id": data.get("id", outline_id),
                            "title": data.get("title", "Untitled Outline"),
                            "description": data.get("description"),
                            "metadata": data.get("metadata", {})
                        })
                    except Exception as e:
                        logger.error(f"Error reading outline file {file}: {e}")
        except Exception as e:
            logger.error(f"Error listing outlines: {e}")
        
        return result
    
    def validate_outline(self, outline: Outline) -> Dict[str, Any]:
        """
        Validate outline against SESATS standards
        
        Args:
            outline: Outline to validate
            
        Returns:
            Validation results
        """
        return self.parser.validate_against_sesats(outline)
    
    def get_node_by_id(self, outline: Outline, node_id: str) -> Optional[OutlineNode]:
        """
        Get a node from an outline by ID
        
        Args:
            outline: Outline to search
            node_id: ID of node to find
            
        Returns:
            Node or None if not found
        """
        return outline.find_node_by_id(node_id)
    
    def create_question_from_node(self, 
                                node: OutlineNode, 
                                template_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a question from an outline node
        
        Args:
            node: Node to create question from
            template_id: Optional template ID to use
            
        Returns:
            Question data
        """
        # This is a placeholder - actual implementation would use the question generation agent
        return {
            "node_id": node.id,
            "node_title": node.title,
            "node_type": node.type,
            "question": {
                "text": f"Question about {node.title}",
                "type": "multiple_choice",
                "options": [
                    {"text": "Option A", "correct": True},
                    {"text": "Option B", "correct": False},
                    {"text": "Option C", "correct": False}
                ]
            }
        } 