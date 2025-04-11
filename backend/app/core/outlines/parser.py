"""
Parser for medical education outlines
"""
from typing import Dict, List, Optional, Union, Any, Tuple
import re
import uuid
import logging
from enum import Enum

from backend.app.core.outlines.models import (
    Outline, OutlineNode, OutlineNodeType, OutlineMetadata
)
from backend.app.core.system_rules.rules import SESATSRules

# Setup logger
logger = logging.getLogger("app.core.outlines.parser")

class OutlineFormat(str, Enum):
    """Supported outline formats"""
    MARKDOWN = "markdown"
    BULLET = "bullet"
    NUMBERED = "numbered"
    INDENTED = "indented"
    JSON = "json"

class OutlineParser:
    """
    Parser for medical education outlines
    
    This class provides functionality to parse outlines in various formats
    into a structured Outline object.
    """
    
    def __init__(self):
        """Initialize outline parser"""
        self.sesats_rules = SESATSRules()
    
    def parse(self, 
             content: str, 
             format: OutlineFormat = OutlineFormat.MARKDOWN,
             title: Optional[str] = None,
             metadata: Optional[Dict[str, Any]] = None) -> Outline:
        """
        Parse outline content into an Outline object
        
        Args:
            content: Raw outline content
            format: Format of the content
            title: Optional title (extracted from content if not provided)
            metadata: Optional metadata
            
        Returns:
            Parsed Outline object
        """
        if format == OutlineFormat.MARKDOWN:
            return self._parse_markdown(content, title, metadata)
        elif format == OutlineFormat.BULLET:
            return self._parse_bullet(content, title, metadata)
        elif format == OutlineFormat.NUMBERED:
            return self._parse_numbered(content, title, metadata)
        elif format == OutlineFormat.INDENTED:
            return self._parse_indented(content, title, metadata)
        elif format == OutlineFormat.JSON:
            return self._parse_json(content, title, metadata)
        else:
            raise ValueError(f"Unsupported outline format: {format}")
    
    def _parse_markdown(self, 
                       content: str, 
                       title: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Outline:
        """
        Parse Markdown outline
        
        Args:
            content: Markdown content
            title: Optional title
            metadata: Optional metadata
            
        Returns:
            Parsed Outline object
        """
        lines = content.strip().split('\n')
        
        # Extract title from first heading if not provided
        if not title and lines and lines[0].startswith('#'):
            title = lines[0].lstrip('#').strip()
            lines = lines[1:]
        elif not title:
            title = "Untitled Outline"
        
        # Create outline
        outline_id = str(uuid.uuid4())
        outline = Outline.create_empty(outline_id, title)
        
        # Add metadata if provided
        if metadata:
            outline.metadata = OutlineMetadata(**metadata)
        
        # Parse content
        current_node = outline.root
        current_level = 0
        
        # Stack to keep track of parent nodes at each level
        node_stack = [current_node]
        
        for line in lines:
            if not line.strip():
                continue
                
            # Check if it's a heading
            if line.startswith('#'):
                level = len(re.match(r'^#+', line).group())
                text = line.lstrip('#').strip()
                
                # Determine node type based on level
                node_type = self._get_node_type_for_level(level)
                
                # Create node
                node_id = str(uuid.uuid4())
                node = OutlineNode(
                    id=node_id,
                    title=text,
                    type=node_type
                )
                
                # Adjust stack if needed
                while len(node_stack) > level:
                    node_stack.pop()
                
                while len(node_stack) < level:
                    node_stack.append(node_stack[-1])
                
                # Add to parent
                parent = node_stack[-1]
                parent.add_child(node)
                
                # Update stack
                node_stack[level-1] = node
                
            # Check if it's a bullet point
            elif line.strip().startswith(('- ', '* ', '+ ')):
                text = line.strip()[2:].strip()
                
                # Create node
                node_id = str(uuid.uuid4())
                node = OutlineNode(
                    id=node_id,
                    title=text,
                    type=OutlineNodeType.POINT
                )
                
                # Add to current node
                current_node.add_child(node)
                
            # Otherwise, treat as content for the current node
            else:
                if current_node.content:
                    current_node.content += '\n' + line
                else:
                    current_node.content = line
        
        return outline
    
    def _parse_bullet(self, 
                     content: str, 
                     title: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> Outline:
        """
        Parse bullet-point outline
        
        Args:
            content: Bullet-point content
            title: Optional title
            metadata: Optional metadata
            
        Returns:
            Parsed Outline object
        """
        lines = content.strip().split('\n')
        
        # Extract title from first line if not provided
        if not title and lines:
            title = lines[0].strip()
            lines = lines[1:]
        elif not title:
            title = "Untitled Outline"
        
        # Create outline
        outline_id = str(uuid.uuid4())
        outline = Outline.create_empty(outline_id, title)
        
        # Add metadata if provided
        if metadata:
            outline.metadata = OutlineMetadata(**metadata)
        
        # Parse content
        current_node = outline.root
        current_level = 0
        
        # Stack to keep track of parent nodes at each level
        node_stack = [current_node]
        
        for line in lines:
            if not line.strip():
                continue
                
            # Check indentation level (based on leading spaces)
            indent_match = re.match(r'^(\s*)([-*+•])\s+(.*?)$', line)
            if indent_match:
                indent = indent_match.group(1)
                text = indent_match.group(3).strip()
                level = len(indent) // 2 + 1  # Assuming 2 spaces per level
                
                # Determine node type based on level
                node_type = self._get_node_type_for_level(level)
                
                # Create node
                node_id = str(uuid.uuid4())
                node = OutlineNode(
                    id=node_id,
                    title=text,
                    type=node_type
                )
                
                # Adjust stack if needed
                while len(node_stack) > level:
                    node_stack.pop()
                
                while len(node_stack) < level:
                    node_stack.append(node_stack[-1])
                
                # Add to parent
                parent = node_stack[-1]
                parent.add_child(node)
                
                # Update stack
                if len(node_stack) == level:
                    node_stack[-1] = node
                else:
                    node_stack.append(node)
            else:
                # If not a bullet point, treat as content for the current node
                if current_node.content:
                    current_node.content += '\n' + line
                else:
                    current_node.content = line
        
        return outline
    
    def _parse_numbered(self, 
                       content: str, 
                       title: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Outline:
        """
        Parse numbered outline
        
        Args:
            content: Numbered outline content
            title: Optional title
            metadata: Optional metadata
            
        Returns:
            Parsed Outline object
        """
        lines = content.strip().split('\n')
        
        # Extract title from first line if not provided
        if not title and lines:
            title = lines[0].strip()
            lines = lines[1:]
        elif not title:
            title = "Untitled Outline"
        
        # Create outline
        outline_id = str(uuid.uuid4())
        outline = Outline.create_empty(outline_id, title)
        
        # Add metadata if provided
        if metadata:
            outline.metadata = OutlineMetadata(**metadata)
        
        # Parse content
        current_node = outline.root
        
        # Dictionary to keep track of parent nodes at each level
        level_nodes = {0: current_node}
        
        for line in lines:
            if not line.strip():
                continue
                
            # Check if it's a numbered line (e.g., "1.", "1.2.3.")
            numbered_match = re.match(r'^(\s*)(\d+(\.\d+)*)\.\s+(.*?)$', line)
            if numbered_match:
                indent = numbered_match.group(1)
                numbers = numbered_match.group(2)
                text = numbered_match.group(4).strip()
                
                # Calculate level from the numbering (e.g., "1.2.3" -> level 3)
                level = len(numbers.split('.'))
                
                # Determine node type based on level
                node_type = self._get_node_type_for_level(level)
                
                # Create node
                node_id = str(uuid.uuid4())
                node = OutlineNode(
                    id=node_id,
                    title=text,
                    type=node_type
                )
                
                # Find parent node
                parent_level = level - 1
                parent = level_nodes.get(parent_level, current_node)
                
                # Add to parent
                parent.add_child(node)
                
                # Update level_nodes
                level_nodes[level] = node
                
                # Remove any deeper levels
                for l in list(level_nodes.keys()):
                    if l > level:
                        del level_nodes[l]
            else:
                # If not a numbered line, treat as content for the current node
                current = level_nodes.get(max(level_nodes.keys()), current_node)
                if current.content:
                    current.content += '\n' + line
                else:
                    current.content = line
        
        return outline
    
    def _parse_indented(self, 
                       content: str, 
                       title: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Outline:
        """
        Parse indented outline
        
        Args:
            content: Indented outline content
            title: Optional title
            metadata: Optional metadata
            
        Returns:
            Parsed Outline object
        """
        lines = content.strip().split('\n')
        
        # Extract title from first non-indented line if not provided
        if not title and lines:
            for line in lines:
                if line.strip() and not line.startswith(' '):
                    title = line.strip()
                    lines.remove(line)
                    break
        
        if not title:
            title = "Untitled Outline"
        
        # Create outline
        outline_id = str(uuid.uuid4())
        outline = Outline.create_empty(outline_id, title)
        
        # Add metadata if provided
        if metadata:
            outline.metadata = OutlineMetadata(**metadata)
        
        # Parse content
        current_node = outline.root
        
        # Stack to keep track of parent nodes at each level
        node_stack = [(0, current_node)]
        
        for line in lines:
            if not line.strip():
                continue
                
            # Calculate indentation level
            indent_match = re.match(r'^(\s*)(.*?)$', line)
            indent = indent_match.group(1)
            text = indent_match.group(2).strip()
            level = len(indent) // 2  # Assuming 2 spaces per level
            
            # Determine node type based on level
            node_type = self._get_node_type_for_level(level)
            
            # Create node
            node_id = str(uuid.uuid4())
            node = OutlineNode(
                id=node_id,
                title=text,
                type=node_type
            )
            
            # Find parent node
            while node_stack and node_stack[-1][0] >= level:
                node_stack.pop()
            
            if not node_stack:
                # If stack is empty, add to root
                outline.root.add_child(node)
                node_stack.append((level, node))
            else:
                # Add to parent
                parent = node_stack[-1][1]
                parent.add_child(node)
                node_stack.append((level, node))
        
        return outline
    
    def _parse_json(self, 
                   content: str, 
                   title: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> Outline:
        """
        Parse JSON outline
        
        Args:
            content: JSON outline content
            title: Optional title (overrides title in JSON)
            metadata: Optional metadata (merged with metadata in JSON)
            
        Returns:
            Parsed Outline object
        """
        import json
        
        try:
            data = json.loads(content)
            
            # Use provided title if available, otherwise use from JSON
            outline_title = title or data.get("title", "Untitled Outline")
            
            # Create outline
            outline_id = data.get("id", str(uuid.uuid4()))
            outline = Outline(
                id=outline_id,
                title=outline_title,
                description=data.get("description"),
                root=self._parse_json_node(data.get("root", {})),
                metadata=OutlineMetadata(**(data.get("metadata", {}) or {}))
            )
            
            # Merge with provided metadata if available
            if metadata:
                # Update outline metadata with provided values
                outline_meta_dict = outline.metadata.dict()
                outline_meta_dict.update(metadata)
                outline.metadata = OutlineMetadata(**outline_meta_dict)
            
            return outline
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON outline: {e}")
            # Fallback to markdown parsing
            return self._parse_markdown(content, title, metadata)
    
    def _parse_json_node(self, node_data: Dict[str, Any]) -> OutlineNode:
        """
        Parse JSON node data
        
        Args:
            node_data: JSON node data
            
        Returns:
            Parsed OutlineNode
        """
        if not node_data:
            # Create default root node if none provided
            return OutlineNode(
                id=str(uuid.uuid4()),
                title="Root",
                type=OutlineNodeType.ROOT
            )
        
        # Create node
        node = OutlineNode(
            id=node_data.get("id", str(uuid.uuid4())),
            title=node_data.get("title", "Untitled"),
            type=OutlineNodeType(node_data.get("type", "section")),
            content=node_data.get("content"),
            metadata=OutlineMetadata(**(node_data.get("metadata", {}) or {})),
            parent_id=node_data.get("parent_id")
        )
        
        # Parse children
        for child_data in node_data.get("children", []):
            child = self._parse_json_node(child_data)
            node.add_child(child)
        
        return node
    
    def _get_node_type_for_level(self, level: int) -> OutlineNodeType:
        """
        Determine node type based on level
        
        Args:
            level: Outline level (1-based)
            
        Returns:
            Appropriate node type
        """
        if level == 0:
            return OutlineNodeType.ROOT
        elif level == 1:
            return OutlineNodeType.SECTION
        elif level == 2:
            return OutlineNodeType.TOPIC
        elif level == 3:
            return OutlineNodeType.SUBTOPIC
        elif level == 4:
            return OutlineNodeType.CONCEPT
        elif level == 5:
            return OutlineNodeType.OBJECTIVE
        else:
            return OutlineNodeType.POINT
    
    def validate_against_sesats(self, outline: Outline) -> Dict[str, Any]:
        """
        Validate outline against SESATS standards
        
        Args:
            outline: Outline to validate
            
        Returns:
            Validation results
        """
        # Get SESATS guidelines
        guidelines = self.sesats_rules.get_guidelines()
        
        # Validation results
        results = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "stats": {
                "total_nodes": 0,
                "sections": 0,
                "topics": 0,
                "subtopics": 0,
                "points": 0
            }
        }
        
        # Check if the outline has a root node
        if not outline.root:
            results["valid"] = False
            results["issues"].append("Outline has no root node")
            return results
        
        # Check if the outline has a title
        if not outline.title:
            results["valid"] = False
            results["issues"].append("Outline has no title")
        
        # Traverse the outline and validate each node
        self._validate_node(outline.root, results, guidelines)
        
        return results
    
    def _validate_node(self, 
                      node: OutlineNode, 
                      results: Dict[str, Any],
                      guidelines: Any,
                      depth: int = 0) -> None:
        """
        Validate a node against SESATS standards
        
        Args:
            node: Node to validate
            results: Validation results to update
            guidelines: SESATS guidelines
            depth: Current depth in the outline
        """
        # Increment counters
        results["stats"]["total_nodes"] += 1
        
        if node.type == OutlineNodeType.SECTION:
            results["stats"]["sections"] += 1
        elif node.type == OutlineNodeType.TOPIC:
            results["stats"]["topics"] += 1
        elif node.type == OutlineNodeType.SUBTOPIC:
            results["stats"]["subtopics"] += 1
        elif node.type == OutlineNodeType.POINT:
            results["stats"]["points"] += 1
        
        # Check node title
        if not node.title:
            results["valid"] = False
            results["issues"].append(f"Node {node.id} has no title")
        
        # Validate node content
        if node.content:
            # Check for specific SESATS guidelines in content
            pass
        
        # Recursively validate children
        for child in node.children:
            self._validate_node(child, results, guidelines, depth + 1) 